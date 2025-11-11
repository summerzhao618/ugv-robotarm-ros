#!/usr/bin/env python3

"""
Launch joystick teleoperation for Husky mobile base
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # Declare arguments
    joy_dev_arg = DeclareLaunchArgument(
        'joy_dev',
        default_value='/dev/input/js0',
        description='Joystick device'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    config_filepath_arg = DeclareLaunchArgument(
        'config_filepath',
        default_value='',
        description='Path to teleop config file (optional)'
    )

    # Joy node
    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        parameters=[{
            'dev': LaunchConfiguration('joy_dev'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
    )

    # Teleop twist joy node
    teleop_twist_joy_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy_node',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'enable_button': 4,  # L1 button (PS4) / LB (Xbox)
            'axis_linear.x': 1,  # Left stick vertical
            'axis_angular.yaw': 0,  # Left stick horizontal
            'scale_linear.x': 0.5,
            'scale_angular.yaw': 1.0,
        }],
        remappings=[
            ('/cmd_vel', '/cmd_vel_joy')  # twist_mux will handle this
        ],
    )

    return LaunchDescription([
        joy_dev_arg,
        use_sim_time_arg,
        config_filepath_arg,
        joy_node,
        teleop_twist_joy_node,
    ])
