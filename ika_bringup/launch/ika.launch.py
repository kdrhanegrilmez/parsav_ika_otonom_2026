import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_ika_gazebo = get_package_share_directory('ika_gazebo')
    pkg_ika_description = get_package_share_directory('ika_description')
    pkg_ika_bringup = get_package_share_directory('ika_bringup')
    
    world_file = os.path.join(pkg_ika_gazebo, 'worlds', 'teknofest_parkur.world')
    urdf_file = os.path.join(pkg_ika_description, 'urdf', 'ika.urdf')
    nav2_params_file = os.path.join(pkg_ika_bringup, 'config', 'nav2_params.yaml')
    ekf_params_file = os.path.join(pkg_ika_bringup, 'config', 'ekf.yaml')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # Gazebo Server and Client
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )
    
    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # Robot State Publisher
    robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # Spawn Robot
    spawn_entity_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'ika', '-file', urdf_file, '-x', '0', '-y', '0', '-z', '0.5'],
        output='screen'
    )

    # Robot Localization (EKF)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_params_file]
    )

    # Tabela Detector Node (Perception)
    tabela_node = Node(
        package='ika_perception',
        executable='tabela_detector',
        name='tabela_detector',
        output='screen'
    )

    # LiDAR Processor Node (Perception)
    lidar_processor_node = Node(
        package='ika_perception',
        executable='lidar_processor',
        name='lidar_processor',
        output='screen'
    )

    # Mission Manager Node (FSM)
    mission_manager_node = Node(
        package='ika_mission_manager',
        executable='mission_manager',
        name='mission_manager',
        output='screen'
    )

    return LaunchDescription([
        gzserver_cmd,
        gzclient_cmd,
        robot_state_publisher_cmd,
        spawn_entity_cmd,
        ekf_node,
        tabela_node,
        lidar_processor_node,
        mission_manager_node
    ])
