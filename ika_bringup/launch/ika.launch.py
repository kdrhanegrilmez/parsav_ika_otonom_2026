import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_ika_description = get_package_share_directory('ika_description')
    pkg_ika_bringup = get_package_share_directory('ika_bringup')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    urdf_file = os.path.join(pkg_ika_description, 'urdf', 'ika.urdf')
    # Jazzy'de basit bir dünya ile başlayalım (boş zemin + güneş)
    
    # Robot State Publisher
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}]
    )

    # Gazebo Sim (Harmonic/Jazzy)
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # Spawn Robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', urdf_file, '-name', 'ika', '-z', '0.5'],
        output='screen'
    )

    # Bridge (ROS 2 <-> Gazebo Sim)
    # Jazzy'de köprü (bridge) çok kritiktir.
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/imu/data@sensor_msgs/msg/Imu@gz.msgs.IMU',
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image'
        ],
        output='screen'
    )

    # Mission nodes
    mission_manager = Node(package='ika_mission_manager', executable='mission_manager', output='screen')
    watchdog = Node(package='ika_mission_manager', executable='watchdog_node', output='screen')
    tabela_node = Node(package='ika_perception', executable='tabela_detector', output='screen')
    lidar_node = Node(package='ika_perception', executable='lidar_processor', output='screen')

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        bridge,
        mission_manager,
        watchdog,
        tabela_node,
        lidar_node
    ])
