#!/usr/bin/env python3

"""
Launch Gazebo with Husky + UR3 + Gripper mobile manipulator
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get package directories
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_husky_ur3_gazebo = get_package_share_directory('husky_ur3_gazebo')

    # Declare arguments
    world_file_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_husky_ur3_gazebo, 'worlds', 'HRI_lab.world'),
        description='Path to world file'
    )

    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Start Gazebo with GUI'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    x_arg = DeclareLaunchArgument('x', default_value='0.0')
    y_arg = DeclareLaunchArgument('y', default_value='0.0')
    z_arg = DeclareLaunchArgument('z', default_value='0.0')
    yaw_arg = DeclareLaunchArgument('yaw', default_value='0.0')

    laser_enabled_arg = DeclareLaunchArgument(
        'laser_enabled',
        default_value='true',
        description='Enable laser scanner'
    )

    camera_h_enabled_arg = DeclareLaunchArgument(
        'camera_h_enabled',
        default_value='true',
        description='Enable head-mounted camera'
    )

    # Launch Gazebo server
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'pause': 'false',
        }.items()
    )

    # Launch Gazebo client
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        ),
        condition=IfCondition(LaunchConfiguration('gui'))
    )

    # Include robot spawner
    robot_spawner = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_husky_ur3_gazebo, 'launch', 'spawn_robot.launch.py')
        ),
        launch_arguments={
            'x': LaunchConfiguration('x'),
            'y': LaunchConfiguration('y'),
            'z': LaunchConfiguration('z'),
            'yaw': LaunchConfiguration('yaw'),
            'laser_enabled': LaunchConfiguration('laser_enabled'),
            'camera_h_enabled': LaunchConfiguration('camera_h_enabled'),
        }.items()
    )

    return LaunchDescription([
        world_file_arg,
        gui_arg,
        use_sim_time_arg,
        x_arg,
        y_arg,
        z_arg,
        yaw_arg,
        laser_enabled_arg,
        camera_h_enabled_arg,
        gzserver,
        gzclient,
        robot_spawner,
    ])
