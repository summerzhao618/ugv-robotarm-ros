#!/usr/bin/env python3

"""
Spawn Husky + UR3 + Gripper robot in Gazebo and start controllers
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Get package directory
    pkg_husky_ur3_gazebo = get_package_share_directory('husky_ur3_gazebo')

    # Declare arguments
    x_arg = DeclareLaunchArgument('x', default_value='0.0')
    y_arg = DeclareLaunchArgument('y', default_value='0.0')
    z_arg = DeclareLaunchArgument('z', default_value='0.0')
    yaw_arg = DeclareLaunchArgument('yaw', default_value='0.0')

    laser_enabled_arg = DeclareLaunchArgument(
        'laser_enabled',
        default_value='true'
    )
    camera_h_enabled_arg = DeclareLaunchArgument(
        'camera_h_enabled',
        default_value='true'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true'
    )

    # Get URDF via xacro
    robot_description_content = ParameterValue(
        Command([
            'xacro ',
            os.path.join(pkg_husky_ur3_gazebo, 'urdf', 'husky_ur3_gripper.urdf.xacro'),
            ' laser_enabled:=', LaunchConfiguration('laser_enabled'),
            ' camera_h_enabled:=', LaunchConfiguration('camera_h_enabled'),
        ]),
        value_type=str
    )

    robot_description = {'robot_description': robot_description_content}

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ]
    )

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'husky_ur3',
            '-topic', 'robot_description',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', LaunchConfiguration('z'),
            '-Y', LaunchConfiguration('yaw'),
        ],
        output='screen',
    )

    # Controller Manager
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            robot_description,
            os.path.join(pkg_husky_ur3_gazebo, 'config', 'control.yaml'),
        ],
        output='screen',
    )

    # Joint State Broadcaster
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    # Diff Drive Controller
    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    # Arm Controller
    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    # Gripper controllers
    gripper_controllers_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'rh_p12_rn_controller',
            'rh_r2_controller',
            'rh_l1_controller',
            'rh_l2_controller',
            '--controller-manager', '/controller_manager'
        ],
        output='screen',
    )

    # Gripper command republisher node
    gripper_publisher = Node(
        package='husky_ur3_gazebo',
        executable='gazebo_rh_pub',
        name='gripper_gazebo_pub',
        output='screen',
    )

    # Twist Mux
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[
            os.path.join(pkg_husky_ur3_gazebo, 'config', 'twist_mux.yaml'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        remappings=[('/cmd_vel_out', '/diff_drive_controller/cmd_vel_unstamped')],
        output='screen',
    )

    # Robot Localization (EKF)
    robot_localization = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_localization',
        parameters=[
            os.path.join(pkg_husky_ur3_gazebo, 'config', 'localization.yaml'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        output='screen',
    )

    # Event handlers for sequential controller spawning
    spawn_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    spawn_diff_drive_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_controller_spawner],
        )
    )

    spawn_arm_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=diff_drive_controller_spawner,
            on_exit=[arm_controller_spawner],
        )
    )

    spawn_gripper_controllers = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=arm_controller_spawner,
            on_exit=[gripper_controllers_spawner],
        )
    )

    return LaunchDescription([
        x_arg,
        y_arg,
        z_arg,
        yaw_arg,
        laser_enabled_arg,
        camera_h_enabled_arg,
        use_sim_time_arg,
        robot_state_publisher,
        spawn_robot,
        controller_manager,
        spawn_joint_state_broadcaster,
        spawn_diff_drive_controller,
        spawn_arm_controller,
        spawn_gripper_controllers,
        gripper_publisher,
        twist_mux,
        robot_localization,
    ])
