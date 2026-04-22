import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_ika_description = get_package_share_directory('ika_description')
    pkg_ika_bringup = get_package_share_directory('ika_bringup')
    pkg_ika_gazebo = get_package_share_directory('ika_gazebo')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    
    urdf_file = os.path.join(pkg_ika_description, 'urdf', 'ika.urdf')
    world_file = os.path.join(pkg_ika_gazebo, 'worlds', 'parkur.world')
    
    # MODIFIED: Adding absolute paths to models AND meshes for textures
    models_path = os.path.join(pkg_ika_gazebo, 'models')
    meshes_path = os.path.join(pkg_ika_gazebo, 'models', 'parkur', 'meshes')
    
    # Robot State Publisher
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # Gazebo Sim
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        # '-v 4' adds verbose logging to see exactly why textures fail
        launch_arguments={'gz_args': f'-r -v 4 {world_file}'}.items()
    )

    # Spawn Robot - Adjusted coordinates to be safer (Z=1.5)
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', urdf_file, '-name', 'ika', '-x', '0', '-y', '0', '-z', '1.5'],
        output='screen'
    )

    # Bridge
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

    return LaunchDescription([
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', models_path),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', meshes_path),
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        bridge
    ])
