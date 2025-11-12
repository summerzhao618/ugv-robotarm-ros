#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Get package directories
    pkg_husky_ur3_gazebo = FindPackageShare('husky_ur3_gazebo')
    pkg_gazebo_ros = FindPackageShare('gazebo_ros')

    # Paths
    urdf_file = PathJoinSubstitution([pkg_husky_ur3_gazebo, 'urdf', 'husky_ur3_gripper.urdf.xacro'])
    world_file = PathJoinSubstitution([pkg_husky_ur3_gazebo, 'worlds', 'HRI_lab.world'])
    empty_urdf = PathJoinSubstitution([pkg_husky_ur3_gazebo, 'urdf', 'empty.urdf'])

    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Process the URDF file using xacro
    robot_description_content = Command([
        'xacro ',
        urdf_file,
        ' robot_namespace:=/',
        ' urdf_extras:=',
        empty_urdf
    ])

    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description_content
        }]
    )

    # Joint state publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Gazebo server
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_gazebo_ros, 'launch', 'gzserver.launch.py'])
        ),
        launch_arguments={
            'world': world_file,
            'verbose': 'true'
        }.items()
    )

    # Gazebo client
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_gazebo_ros, 'launch', 'gzclient.launch.py'])
        )
    )

    # Spawn entity
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'husky_ur3',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ]
    )

    # RViz2
    rviz_config_file = PathJoinSubstitution([pkg_husky_ur3_gazebo, 'config', 'view_robot.rviz'])
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=None  # Always launch, but you can make this conditional
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        robot_state_publisher_node,
        joint_state_publisher_node,
        gzserver,
        gzclient,
        spawn_entity,
        rviz_node,
    ])
