import rclpy
from rclpy.node import Node
from enum import Enum
import time
import math

from ika_interfaces.msg import TabelaTespit, AtisDurumu, AracDurumu, EngelDurumu
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist

class MissionState(Enum):
    INIT = 1
    NAVIGATING = 2
    WAIT_ON_SLOPE = 3  # %45 Eğimde 2 sn bekleme
    OBSTACLE_AVOIDANCE = 4 # Kayar engel tespiti
    ATIS_BOLGESI = 5 # Atış tabelası görüldü
    FIRING = 6 # Ateş ediliyor
    EMERGENCY_STOP = 7

class MissionManager(Node):
    def __init__(self):
        super().__init__('mission_manager')
        self.get_logger().info('PARSAV İKA Görev Yöneticisi Başlatıldı.')
        
        self.state = MissionState.INIT
        self.pitch = 0.0
        self.last_slope_time = 0.0
        
        # Yayıncılar ve Aboneler
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.status_pub = self.create_publisher(AracDurumu, 'arac_durumu', 10)
        
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(TabelaTespit, 'tabela_tespit', self.tabela_cb, 10)
        self.create_subscription(AtisDurumu, 'atis_durumu', self.atis_cb, 10)
        self.create_subscription(EngelDurumu, 'kayar_engel_durumu', self.engel_cb, 10)
        self.create_subscription(Twist, 'cmd_vel_nav', self.nav_cmd_cb, 10)

        self.timer = self.create_timer(0.1, self.control_loop)
        self.state = MissionState.NAVIGATING

    def imu_cb(self, msg):
        # Pitch açısı hesapla (Rampa tespiti)
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
                self.get_logger().info('HEDEF KİLİTLENDİ! ATEŞ!')

    def engel_cb(self, msg):
        # Kayar engel yaklaşımı analizi (Basitleştirilmiş)
        if abs(msg.tahmini_konum_x) < 2.0:
            self.get_logger().warn('Hareketi Engel Tespit Edildi! Hız kesiliyor.')

    def nav_cmd_cb(self, msg):
        self.last_nav_msg = msg

    def control_loop(self):
        cmd = Twist()
        
        if self.state == MissionState.NAVIGATING:
            if abs(self.pitch) > 24.0: # %45 eğim ~24 derece
                self.state = MissionState.WAIT_ON_SLOPE
                self.last_slope_time = time.time()
                self.get_logger().info('Rampada Duruluyor (2sn bekleme)...')
            else:
                # Nav2'den gelen komutu aynen ilet (burada self.last_nav_msg kullanılabilir)
                pass 
                
        elif self.state == MissionState.WAIT_ON_SLOPE:
            if time.time() - self.last_slope_time > 2.0:
                self.state = MissionState.NAVIGATING
                self.get_logger().info('Bekleme Bitti, Devam Ediliyor.')
            else:
                cmd.linear.x = 0.0 # Dur
                
        elif self.state == MissionState.FIRING:
            # 1 sn ateş et sonra devam et
            time.sleep(1.0)
            self.state = MissionState.NAVIGATING
            
        self.cmd_vel_pub.publish(cmd)
        
        # Durum mesajı yayınla
        status = AracDurumu()
        status.mod = self.state.name
        self.status_pub.publish(status)

def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
