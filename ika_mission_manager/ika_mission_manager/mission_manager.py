import rclpy
from rclpy.node import Node
from enum import Enum
import time
import math

from ika_interfaces.msg import TabelaTespit, AtisDurumu, AracDurumu, EngelDurumu
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist, PoseStamped
from rclpy.duration import Duration
from std_msgs.msg import Empty, Bool
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose

class MissionState(Enum):
    IDLE = 1
    NAVIGATING = 2
    WAIT_ON_SLOPE = 3
    ATIS_BOLGESI = 5
    FIRING = 6
    FINISHED = 8

class MissionManager(Node):
    def __init__(self):
        super().__init__('mission_manager')
        self.get_logger().info('PARSAV İKA OTO-PİLOT (v3.0) Başlatıldı.')
        
        self.state = MissionState.IDLE
        self.pitch = 0.0
        self.start_wait_time = self.get_clock().now()
        
        # Nav2 Action Client (Hedef Göndermek İçin)
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Parkur Waypointleri (Haritaya göre tahmini x, y koordinatları)
        # 1: Rampa Önü, 2: Engel Bölgesi, 3: Atış Bölgesi, 4: Bitiş
        self.waypoints = [
            (5.0, 0.0),   # 5 metre ileri
            (15.0, 0.0),  # Rampa civarı
            (25.0, 0.0),  # Atış bölgesi
            (32.0, 0.0)   # Bitiş çizgisi
        ]
        self.current_waypoint_idx = 0

        # Yayıncılar
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.heartbeat_pub = self.create_publisher(Empty, 'mission_heartbeat', 10)
        
        # Aboneler
        self.create_subscription(Bool, '/mission_start', self.start_mission_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(TabelaTespit, 'tabela_tespit', self.tabela_cb, 10)
        self.create_subscription(AtisDurumu, 'atis_durumu', self.atis_cb, 10)

        self.last_nav_msg = Twist()
        self.timer = self.create_timer(0.1, self.control_loop)
        self.hb_timer = self.create_timer(0.2, self.publish_heartbeat)

    def start_mission_cb(self, msg):
        if msg.data and self.state == MissionState.IDLE:
            self.get_logger().info('--- OTO-PİLOT DEVREDE: PARKURA BAŞLANIYOR! ---')
            self.state = MissionState.NAVIGATING
            self.send_next_waypoint()

    def send_next_waypoint(self):
        if self.current_waypoint_idx < len(self.waypoints):
            x, y = self.waypoints[self.current_waypoint_idx]
            self.get_logger().info(f'Hedef Waypoint Gönderiliyor: {x}, {y}')
            
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose.header.frame_id = 'map'
            goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
            goal_msg.pose.pose.position.x = x
            goal_msg.pose.pose.position.y = y
            goal_msg.pose.pose.orientation.w = 1.0
            
            self.nav_to_pose_client.wait_for_server()
            self._send_goal_future = self.nav_to_pose_client.send_goal_async(goal_msg)
            self._send_goal_future.add_done_callback(self.goal_response_callback)
        else:
            self.state = MissionState.FINISHED
            self.get_logger().info('--- PARKUR TAMAMLANDI! ---')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Hedef reddedildi!')
            return
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        self.get_logger().info('Waypoint ulaşıldı, bir sonrakine geçiliyor...')
        self.current_waypoint_idx += 1
        if self.state == MissionState.NAVIGATING:
            self.send_next_waypoint()

    def publish_heartbeat(self):
        self.heartbeat_pub.publish(Empty())

    def imu_cb(self, msg):
        sinp = 2 * (msg.orientation.w * msg.orientation.y - msg.orientation.z * msg.orientation.x)
        sinp = max(-1.0, min(1.0, sinp))
        self.pitch = math.degrees(math.asin(sinp))

    def tabela_cb(self, msg):
        if msg.id == 10 and self.state == MissionState.NAVIGATING:
            # Atış bölgesi tabelası, hedefi durdurup kilitlenmeye geçebiliriz
            # (Şimdilik oto-pilot devam etsin, gerekirse buraya 'cancel_goal' eklenir)
            pass

    def atis_cb(self, msg):
        if msg.hedef_kilitlendi and abs(msg.x_hata) < 0.05:
            # Atış anında otonom sürüşü durdurabiliriz
            pass

    def control_loop(self):
        # Nav2 şu an asıl sürüşü NavigateToPose üzerinden yapıyor.
        # Mission Manager sadece kritik durumlarda (Rampa vb.) müdahale eder.
        if self.state == MissionState.WAIT_ON_SLOPE:
            elapsed = self.get_clock().now() - self.start_wait_time
            if elapsed > Duration(seconds=2):
                self.state = MissionState.NAVIGATING
                self.get_logger().info('Bekleme bitti, otonom sürüş devam ediyor.')
            else:
                # Durdurma komutu (cmd_vel üzerinden Nav2'yi eziyoruz)
                stop = Twist()
                self.cmd_vel_pub.publish(stop)
        
        elif self.state == MissionState.NAVIGATING:
            if abs(self.pitch) > 24.0:
                self.state = MissionState.WAIT_ON_SLOPE
                self.start_wait_time = self.get_clock().now()
                self.get_logger().info('RAMPA TESPİT EDİLDİ! Otonom bekleme yapılıyor...')

def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
