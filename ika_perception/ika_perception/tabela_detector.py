import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from ika_interfaces.msg import TabelaTespit, AtisDurumu
import cv2
from cv_bridge import CvBridge
import numpy as np
import os

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

class TabelaDetector(Node):
    def __init__(self):
        super().__init__('tabela_detector')
        self.get_logger().info('PARSAV İKA YOLOv8 Algılayıcı Başlatıldı.')
        
        # Model Yükleme: Önce .engine (TensorRT), yoksa .pt dene
        model_path = 'yolov8n.engine'
        if not os.path.exists(model_path):
            model_path = 'yolov8n.pt'
            
        if YOLO:
            try:
                self.model = YOLO(model_path)
                self.get_logger().info(f'Model yüklendi: {model_path}')
            except Exception as e:
                self.get_logger().error(f'Model yüklenemedi: {e}')
                self.model = None
        else:
            self.get_logger().error('ultralytics kütüphanesi bulunamadı! Algılama yapılamayacak.')
            self.model = None
            
        self.bridge = CvBridge()
        
        self.tabela_pub = self.create_publisher(TabelaTespit, 'tabela_tespit', 10)
        self.atis_pub = self.create_publisher(AtisDurumu, 'atis_durumu', 10)
        
        self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)

    def image_callback(self, msg):
        if self.model is None:
            return

        try:
            # ROS Image -> OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # YOLO Tahmini
            # conf=0.5, device=0 (GPU)
            results = self.model.predict(cv_image, conf=0.5, verbose=False)
            
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Örnek Sınıflandırma (Yarışma modeline göre güncellenmeli)
                    # cls_id 0: Tabela, cls_id 1: Hedef olsun
                    if cls_id == 0:
                        t_msg = TabelaTespit()
                        t_msg.id = 10 # Örnek ID
                        t_msg.guvenilirlik = conf
                        # Bounding box boyutundan mesafe tahmini (Basit)
                        w = box.xywh[0][2]
                        t_msg.mesafe = 100.0 / w # Kalibre edilmeli
                        self.tabela_pub.publish(t_msg)
                        
                    elif cls_id == 1:
                        a_msg = AtisDurumu()
                        a_msg.hedef_kilitlendi = True
                        # Merkezden kaçıklık (x_hata, y_hata)
                        img_h, img_w = cv_image.shape[:2]
                        cx, cy = box.xywh[0][0], box.xywh[0][1]
                        a_msg.x_hata = float((cx - (img_w/2)) / img_w)
                        a_msg.y_hata = float((cy - (img_h/2)) / img_h)
                        self.atis_pub.publish(a_msg)
                        
        except Exception as e:
            self.get_logger().error(f'Görüntü işleme hatası: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = TabelaDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
