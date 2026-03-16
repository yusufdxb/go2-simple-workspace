from setuptools import setup
import os
from glob import glob

package_name = 'go2_voice_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Yusuf Guenena',
    maintainer_email='yusuf.a.guenena@gmail.com',
    description='Voice command interface for Unitree GO2',
    license='MIT',
    entry_points={
        'console_scripts': [
            'speech_command_node = go2_voice_control.speech_command_node:main',
            'go2_command_bridge  = go2_voice_control.go2_command_bridge:main',
        ],
    },
)
