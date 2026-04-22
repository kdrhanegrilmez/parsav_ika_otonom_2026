import rclpy
from rclpy.node import Node
from enum import Enum

# Gerekli özel mesajları içe aktaracağız (derlendikten sonra çalışacak)
# from ika_interfaces.msg import TabelaTespit, AtisDurumu, AracDurumu, EngelDurumu

class MissionState(Enum):
    INIT = 1
    IDLE = 2
    NAVIGATING = 3
    WAIT_ON_SLOPE = 4
    STOPPED = 5
    FIRING = 6
    FAILSAFE = 7
    MANUAL_OVERRIDE = 8

class MissionManagerNode(Node):
    def __init__(self):
        super().__init__('mission_manager_node')
        self.get_logger().info('Mission Manager Node başlatıldı.')
        
        self.current_state = MissionState.INIT
        self.get_logger().info(f'Mevcut Durum: {self.current_state.name}')

        # Subscriber ve Publisher'lar buraya eklenecek
        # Örnek:
        # self.tabela_sub = self.create_subscription(TabelaTespit, 'tabela_tespit', self.tabela_callback, 10)
        # self.arac_durumu_pub = self.create_publisher(AracDurumu, 'arac_durumu', 10)
        
        # Simülasyon/Döngü için timer
        self.timer = self.create_timer(0.1, self.timer_callback) # 10 Hz

        # Init'ten Idle'a geçiş (Sistem kontrolleri başarılı varsayılarak)
        self.change_state(MissionState.IDLE)

    def change_state(self, new_state):
        if self.current_state != new_state:
            self.get_logger().info(f'Durum Değişimi: {self.current_state.name} -> {new_state.name}')
            self.current_state = new_state
            # Durum değişiminde yapılacak özel işlemler buraya eklenebilir

    def timer_callback(self):
        # Durum makinesinin sürekli güncellenen mantığı
        if self.current_state == MissionState.IDLE:
            # Örnek: Start komutu bekleniyor...
            pass
        elif self.current_state == MissionState.NAVIGATING:
            # Otonom sürüş mantığı
            pass
        elif self.current_state == MissionState.FAILSAFE:
            # Güvenli duruş mantığı
            pass

    # def tabela_callback(self, msg):
    #     self.get_logger().info(f'Tabela Algılandı: ID={msg.tabela_id}, Mesafe={msg.mesafe}')
    #     # Tabelaya göre state değiştirme mantığı
    #     if msg.tabela_id == 8: # Su geçişi vb.
    #         self.change_state(MissionState.NAVIGATING) # veya uygun durum

def main(args=None):
    rclpy.init(args=args)
    node = MissionManagerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
