import rclpy
from rclpy.node import Node
from enum import Enum
import time
import math

from ika_interfaces.msg import TabelaTespit, AtisDurumu, AracDurumu, EngelDurumu
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
from rclpy.duration import Duration
from std_msgs.msg import Empty

class MissionState(Enum):
    INIT = 1
    NAVIGATING = 2
    WAIT_ON_SLOPE = 3  # %45 Eğimde 2 sn bekleme
    ATIS_BOLGESI = 5
    FIRING = 6
    EMERGENCY_STOP = 7

class MissionManager(Node):
    def __init__(self):
        super().__init__('mission_manager')
        self.get_logger().info('PARSAV İKA Görev Yöneticisi v2.0 (Asenkron) Başlatıldı.')
        
        self.state = MissionState.NAVIGATING
        self.pitch = 0.0
        self.start_wait_time = self.get_clock().now()
        
        # Yayıncılar ve Aboneler
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.heartbeat_pub = self.create_publisher(Empty, 'mission_heartbeat', 10)
        
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(TabelaTespit, 'tabela_tespit', self.tabela_cb, 10)
        self.create_subscription(AtisDurumu, 'atis_durumu', self.atis_cb, 10)
        self.create_subscription(Twist, 'cmd_vel_nav', self.nav_cmd_cb, 10)

        self.last_nav_msg = Twist()
        
        # Ana Kontrol Döngüsü (10Hz)
        self.timer = self.create_timer(0.1, self.control_loop)
        # Watchdog için Heartbeat (5Hz)
        self.hb_timer = self.create_timer(0.2, self.publish_heartbeat)

    def publish_heartbeat(self):
        self.heartbeat_pub.publish(Empty())

    def imu_cb(self, msg):
        sinp = 2 * (msg.orientation.w * msg.orientation.y - msg.orientation.z * msg.orientation.x)
        self.pitch = math.degrees(math.asin(sinp))

    def tabela_cb(self, msg):
        if msg.id == 10 and self.state == MissionState.NAVIGATING:
            self.state = MissionState.ATIS_BOLGESI
            self.get_logger().info('Atış Bölgesi Algılandı! Duruluyor...')

    def atis_cb(self, msg):
        if self.state == MissionState.ATIS_BOLGESI and msg.hedef_kilitlendi:
            if abs(msg.x_hata) < 0.05:
                self.state = MissionState.FIRING
                self.start_wait_time = self.get_clock().now()
                self.get_logger().info('HEDEF KİLİTLENDİ! ATEŞ!')

    def nav_cmd_cb(self, msg):
        self.last_nav_msg = msg

    def control_loop(self):
        cmd = Twist()
        now = self.get_clock().now()
        
        if self.state == MissionState.NAVIGATING:
            if abs(self.pitch) > 24.0: # %45 eğim tespiti
                self.state = MissionState.WAIT_ON_SLOPE
                self.start_wait_time = now
                self.get_logger().info('Rampada Duruldu (2sn Asenkron Bekleme)...')
            else:
                cmd = self.last_nav_msg
                
        elif self.state == MissionState.WAIT_ON_SLOPE:
            elapsed = now - self.start_wait_time
            if elapsed > Duration(seconds=2):
                self.state = MissionState.NAVIGATING
                self.get_logger().info('Bekleme Bitti, Devam Ediliyor.')
            else:
                cmd.linear.x = 0.0 # Güvenli Duruş
                
        elif self.state == MissionState.ATIS_BOLGESI:
            cmd.linear.x = 0.0 # Hedef aranırken dur
            
        elif self.state == MissionState.FIRING:
            elapsed = now - self.start_wait_time
            if elapsed > Duration(seconds=1): # 1 sn ateş süresi
                self.state = MissionState.NAVIGATING
            else:
                cmd.linear.x = 0.0
            
        self.cmd_vel_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
