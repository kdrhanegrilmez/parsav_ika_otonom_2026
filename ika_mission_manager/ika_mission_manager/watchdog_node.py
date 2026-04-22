import rclpy
from rclpy.node import Node
from std_msgs.msg import Empty
from geometry_msgs.msg import Twist
from rclpy.duration import Duration

class WatchdogNode(Node):
    def __init__(self):
        super().__init__('watchdog_node')
        self.get_logger().warn('PARSAV İKA Watchdog Aktif. Görev Yöneticisi izleniyor...')
        
        self.last_heartbeat = self.get_clock().now()
        
        # Abonelik: Mission Manager'dan gelen kalp atışı
        self.create_subscription(Empty, 'mission_heartbeat', self.heartbeat_cb, 10)
        
        # Yayıncı: Acil durum durdurma sinyali
        self.safe_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # Kontrol Döngüsü: 200ms (5Hz)
        self.create_timer(0.2, self.check_system_health)

    def heartbeat_cb(self, msg):
        self.last_heartbeat = self.get_clock().now()

    def check_system_health(self):
        elapsed = self.get_clock().now() - self.last_heartbeat
        
        # Eğer 0.5 saniyeden fazla süredir kalp atışı gelmiyorsa (Haberleşme kesilmişse)
        if elapsed > Duration(seconds=0.5):
            self.get_logger().error('KRİTİK HATA: Mission Manager kalp atışı kesildi! Acil durdurma uygulanıyor.')
            stop_msg = Twist()
            stop_msg.linear.x = 0.0
            stop_msg.angular.z = 0.0
            self.safe_pub.publish(stop_msg)

def main(args=None):
    rclpy.init(args=args)
    node = WatchdogNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
