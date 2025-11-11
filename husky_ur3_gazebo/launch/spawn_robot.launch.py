#!/usr/bin/env python3

"""
Spawn Husky + UR3 + Gripper robot in Gazebo and start controllers
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


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

    # Process xacro file using Python xacro library (official pattern)
    xacro_file = os.path.join(pkg_husky_ur3_gazebo, 'urdf', 'husky_ur3_gripper.urdf.xacro')
    controller_config_file = os.path.join(pkg_husky_ur3_gazebo, 'config', 'control.yaml')

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc, mappings={
        'laser_enabled': 'true',
        'camera_h_enabled': 'true',
        'control_config_file': controller_config_file
    })
    robot_description = {'robot_description': doc.toxml()}

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': LaunchConfiguration('use_sim_time')}]
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

    # Load controllers using ExecuteProcess (official pattern from gazebo_ros2_control_demos)
    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )

    load_diff_drive_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'diff_drive_controller'],
        output='screen'
    )

    load_arm_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'arm_controller'],
        output='screen'
    )

    load_gripper_controller_1 = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'rh_p12_rn_controller'],
        output='screen'
    )

    load_gripper_controller_2 = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'rh_r2_controller'],
        output='screen'
    )

    load_gripper_controller_3 = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'rh_l1_controller'],
        output='screen'
    )

    load_gripper_controller_4 = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'rh_l2_controller'],
        output='screen'
    )

    # Gripper command republisher node
    gripper_publisher = Node(
        package='husky_ur3_gazebo',
        executable='gazebo_rh_pub',
        name='gripper_gazebo_pub',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
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

    # Delay controller spawning after robot is spawned (give Gazebo time to load)
    delay_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot,
            on_exit=[
                TimerAction(
                    period=2.0,
                    actions=[load_joint_state_broadcaster],
                )
            ],
        )
    )

    delay_diff_drive_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_joint_state_broadcaster,
            on_exit=[load_diff_drive_controller],
        )
    )

    delay_arm_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_diff_drive_controller,
            on_exit=[load_arm_controller],
        )
    )

    delay_gripper_controller_1 = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_arm_controller,
            on_exit=[load_gripper_controller_1],
        )
    )

    delay_gripper_controller_2 = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_gripper_controller_1,
            on_exit=[load_gripper_controller_2],
        )
    )

    delay_gripper_controller_3 = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_gripper_controller_2,
            on_exit=[load_gripper_controller_3],
        )
    )

    delay_gripper_controller_4 = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=load_gripper_controller_3,
            on_exit=[load_gripper_controller_4],
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
        delay_joint_state_broadcaster,
        delay_diff_drive_controller,
        delay_arm_controller,
        delay_gripper_controller_1,
        delay_gripper_controller_2,
        delay_gripper_controller_3,
        delay_gripper_controller_4,
        gripper_publisher,
        twist_mux,
        robot_localization,
    ])
