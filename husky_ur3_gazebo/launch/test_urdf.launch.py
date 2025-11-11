#!/usr/bin/env python3

"""
Test launch file - spawn robot WITHOUT ros2_control to diagnose URDF issues
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Get package directory
    pkg_husky_ur3_gazebo = get_package_share_directory('husky_ur3_gazebo')

    # Declare arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true'
    )

    # Get URDF - temporarily disable cameras to avoid realsense mesh errors
    xacro_file = os.path.join(pkg_husky_ur3_gazebo, 'urdf', 'husky_ur3_gripper.urdf.xacro')

    robot_description_content = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            xacro_file,
            ' ',
            'laser_enabled:=false',
            ' ',
            'camera_h_enabled:=false',
        ]),
        value_type=str
    )

    robot_description = {'robot_description': robot_description_content}

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # Joint State Publisher - publishes default joint states for visualization
    # This is needed because ros2_control is not working properly
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={
            'world': os.path.join(pkg_husky_ur3_gazebo, 'worlds', 'HRI_lab.world'),
            'verbose': 'true'
        }.items()
    )

    # Spawn robot
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'husky_ur3',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5',  # Spawn higher to avoid ground collision
        ],
        output='screen',
    )

    # RViz for visualization
    rviz_config = os.path.join(pkg_husky_ur3_gazebo, 'rviz', 'husky_ur3.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    return LaunchDescription([
        use_sim_time_arg,
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        spawn_robot,
        rviz_node,
    ])
