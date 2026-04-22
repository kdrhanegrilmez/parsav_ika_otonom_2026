from setuptools import setup
import os
from glob import glob

package_name = 'ika_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'scripts'), glob('scripts/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kadir',
    maintainer_email='kadir@todo.todo',
    description='Perception nodes for IKA with TensorRT support',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tabela_detector = ika_perception.tabela_detector:main',
            'lidar_processor = ika_perception.lidar_processor:main',
        ],
    },
)
