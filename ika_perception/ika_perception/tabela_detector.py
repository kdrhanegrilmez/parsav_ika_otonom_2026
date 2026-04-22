import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from ika_interfaces.msg import TabelaTespit, AtisDurumu
import cv2
import numpy as np

class TabelaDetector(Node):
    def __init__(self):
        super().__init__('tabela_detector')
        self.get_logger().info('YOLOv8 Tabela/Hedef Dedektörü Başlatıldı.')
        
        # YOLOv8 Placeholder - Gerçek kullanımda: from ultralytics import YOLO
        # self.model = YOLO('yolov8n.pt') 
        
        self.tabela_pub = self.create_publisher(TabelaTespit, 'tabela_tespit', 10)
        self.atis_pub = self.create_publisher(AtisDurumu, 'atis_durumu', 10)
        
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)

    def image_callback(self, msg):
        # Simülasyonda belirli bir bölgeye gelindiğinde 'sahte' tespitler üretelim
        # Gerçek uygulamada msg (Image) OpenCV'ye çevrilip model.predict() yapılır.
        
        # Örnek: Rastgele Tabela Tespiti (Simülasyon İçin)
        if np.random.rand() > 0.95:
            t_msg = TabelaTespit()
            t_msg.id = 10 # Atış Bölgesi Tabelası
            t_msg.mesafe = 5.0
            t_msg.guvenilirlik = 0.98
            self.tabela_pub.publish(t_msg)
            
        # Örnek: Hedef Tespiti
        a_msg = AtisDurumu()
        a_msg.hedef_kilitlendi = True
        a_msg.x_hata = 0.01 # Merkezde
        a_msg.y_hata = 0.01
        self.atis_pub.publish(a_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TabelaDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
