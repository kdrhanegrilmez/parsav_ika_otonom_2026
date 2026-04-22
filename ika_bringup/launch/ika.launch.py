import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_ika_description = get_package_share_directory('ika_description')
    pkg_ika_bringup = get_package_share_directory('ika_bringup')
    pkg_ika_gazebo = get_package_share_directory('ika_gazebo')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')
    
    urdf_file = os.path.join(pkg_ika_description, 'urdf', 'ika.urdf')
    world_file = os.path.join(pkg_ika_gazebo, 'worlds', 'parkur.world')
    nav_params = os.path.join(pkg_ika_bringup, 'config', 'nav2_params.yaml')
    
    # Paths for Gazebo models and textures
    models_path = os.path.join(pkg_ika_gazebo, 'models')
    
    # Robot State Publisher
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # Gazebo Sim (Harmonic)
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # Spawn Robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', urdf_file, '-name', 'ika', '-x', '0', '-y', '0', '-z', '1.0'],
        output='screen'
    )

    # Bridge (ROS 2 <-> Gazebo Sim)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/imu/data@sensor_msgs/msg/Imu@gz.msgs.IMU',
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock'
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # Nav2 Stack
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')),
        launch_arguments={
            'use_sim_time': 'True',
            'params_file': nav_params,
            'autostart': 'True'
        }.items()
    )

    # SLAM (For mapping and localization)
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')),
        launch_arguments={'use_sim_time': 'True'}.items()
    )

    # Otonom Düğümler (Mission Manager, YOLO, Lidar)
    mission_manager = Node(
        package='ika_mission_manager',
        executable='mission_manager',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    watchdog = Node(
        package='ika_mission_manager',
        executable='watchdog_node',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    tabela_detector = Node(
        package='ika_perception',
        executable='tabela_detector',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    lidar_processor = Node(
        package='ika_perception',
        executable='lidar_processor',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models_path),
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        bridge,
        nav2_launch,
        slam_launch,
        mission_manager,
        watchdog,
        tabela_detector,
        lidar_processor
    ])
