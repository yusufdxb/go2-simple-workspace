"""
GO2 Voice Control — Launch File
Starts both nodes together.

Usage:
  ros2 launch go2_voice_control voice_control_launch.py
  ros2 launch go2_voice_control voice_control_launch.py use_whisper:=true
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_whisper  = LaunchConfiguration('use_whisper')
    device_index = LaunchConfiguration('device_index')

    declare_whisper = DeclareLaunchArgument(
        'use_whisper', default_value='false',
        description='Use Whisper as fallback if Google SR fails'
    )
    declare_device = DeclareLaunchArgument(
        'device_index', default_value='-1',
        description='Microphone device index (-1 = system default)'
    )

    params_file = PathJoinSubstitution([
        FindPackageShare('go2_voice_control'), 'config', 'params.yaml'
    ])

    speech_node = Node(
        package='go2_voice_control',
        executable='speech_command_node',
        name='speech_command_node',
        parameters=[
            params_file,
            {'use_whisper':  use_whisper},
            {'device_index': device_index},
        ],
        output='screen',
    )

    bridge_node = Node(
        package='go2_voice_control',
        executable='go2_command_bridge',
        name='go2_command_bridge',
        output='screen',
    )

    return LaunchDescription([
        declare_whisper,
        declare_device,
        speech_node,
        bridge_node,
    ])
