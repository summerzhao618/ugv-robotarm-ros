#!/usr/bin/env python3

import os
import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def load_yaml(package_name, file_path):
    """Load a YAML file from a package."""
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)

    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None


def launch_setup(context, *args, **kwargs):
    """Setup function to generate launch description with access to context."""

    # Get package directories
    moveit_config_pkg = FindPackageShare('husky_ur3_gripper_moveit_config')
    husky_gazebo_pkg = FindPackageShare('husky_ur3_gazebo')

    # Paths
    urdf_file = PathJoinSubstitution([husky_gazebo_pkg, 'urdf', 'husky_ur3_gripper.urdf.xacro'])
    srdf_file = PathJoinSubstitution([moveit_config_pkg, 'config', 'husky.srdf'])
    kinematics_yaml_file = PathJoinSubstitution([moveit_config_pkg, 'config', 'kinematics.yaml'])
    joint_limits_yaml_file = PathJoinSubstitution([moveit_config_pkg, 'config', 'joint_limits.yaml'])
    ompl_planning_yaml_file = PathJoinSubstitution([moveit_config_pkg, 'config', 'ompl_planning.yaml'])

    # Robot description
    robot_description_content = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ',
            urdf_file,
            ' robot_namespace:=/',
            ' urdf_extras:=',
            PathJoinSubstitution([husky_gazebo_pkg, 'urdf', 'empty.urdf'])
        ]),
        value_type=str
    )

    robot_description = {'robot_description': robot_description_content}

    # Robot semantic description (SRDF)
    robot_description_semantic_content = Command([
        FindExecutable(name='cat'), ' ',
        srdf_file
    ])
    robot_description_semantic = {
        'robot_description_semantic': ParameterValue(robot_description_semantic_content, value_type=str)
    }

    # Kinematics configuration
    kinematics_yaml = load_yaml('husky_ur3_gripper_moveit_config', 'config/kinematics.yaml')
    robot_description_kinematics = {'robot_description_kinematics': kinematics_yaml}

    # Joint limits
    joint_limits_yaml = load_yaml('husky_ur3_gripper_moveit_config', 'config/joint_limits.yaml')
    robot_description_planning = {'robot_description_planning': joint_limits_yaml}

    # Planning configuration
    ompl_planning_yaml = load_yaml('husky_ur3_gripper_moveit_config', 'config/ompl_planning.yaml')
    ompl_planning_pipeline_config = {
        'move_group': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': 'default_planner_request_adapters/AddTimeOptimalParameterization '
                               'default_planner_request_adapters/ResolveConstraintFrames '
                               'default_planner_request_adapters/FixWorkspaceBounds '
                               'default_planner_request_adapters/FixStartStateBounds '
                               'default_planner_request_adapters/FixStartStateCollision '
                               'default_planner_request_adapters/FixStartStatePathConstraints',
            'start_state_max_bounds_error': 0.1
        }
    }
    ompl_planning_pipeline_config['move_group'].update(ompl_planning_yaml)

    # Trajectory execution configuration
    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01
    }

    # Controller configuration for MoveIt
    moveit_controllers = {
        'moveit_simple_controller_manager': {
            'controller_names': ['arm_controller'],
            'arm_controller': {
                'type': 'FollowJointTrajectory',
                'action_ns': 'follow_joint_trajectory',
                'default': True,
                'joints': [
                    'shoulder_pan_joint',
                    'shoulder_lift_joint',
                    'elbow_joint',
                    'wrist_1_joint',
                    'wrist_2_joint',
                    'wrist_3_joint'
                ]
            }
        }
    }

    # Planning scene monitor parameters
    planning_scene_monitor_parameters = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True
    }

    # Launch Gazebo with the robot
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([husky_gazebo_pkg, 'launch', 'test_urdf.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': 'true'
        }.items()
    )

    # Move group node
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            robot_description_planning,
            ompl_planning_pipeline_config,
            trajectory_execution,
            moveit_controllers,
            planning_scene_monitor_parameters,
            {'use_sim_time': True}
        ]
    )

    # RViz node
    rviz_config_file = PathJoinSubstitution([
        moveit_config_pkg,
        'launch',
        'moveit.rviz'
    ])

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        arguments=['-d', rviz_config_file],
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            robot_description_planning,
            {'use_sim_time': True}
        ]
    )

    return [
        gazebo_launch,
        move_group_node,
        rviz_node,
    ]


def generate_launch_description():
    """Generate launch description."""

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        OpaqueFunction(function=launch_setup)
    ])
