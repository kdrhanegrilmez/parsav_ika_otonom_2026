from setuptools import setup
import os
from glob import glob

package_name = 'ika_mission_manager'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kadir',
    maintainer_email='kadir@todo.todo',
    description='TEKNOFEST 2026 IKA Mission Manager with Watchdog',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_manager = ika_mission_manager.mission_manager:main',
            'watchdog_node = ika_mission_manager.watchdog_node:main',
        ],
    },
)
