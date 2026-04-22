import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from ika_interfaces.msg import EngelDurumu
import numpy as np
try:
    from sklearn.cluster import DBSCAN
except ImportError:
    DBSCAN = None

class LidarProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')
        self.get_logger().info('DBSCAN LiDAR Engel İşleyici Başlatıldı.')
        
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.engel_pub = self.create_publisher(EngelDurumu, 'kayar_engel_durumu', 10)
        
        self.gecmis_konumlar = [] # Son 5 konumu tut

    def scan_callback(self, msg):
        # LaserScan verisini kartezyen koordinatlara çevir
        ranges = np.array(msg.ranges)
        angles = np.linspace(msg.angle_min, msg.angle_max, len(ranges))
        
        # Sadece geçerli menzilleri al
        mask = (ranges > msg.range_min) & (ranges < msg.range_max)
        x = ranges[mask] * np.cos(angles[mask])
        y = ranges[mask] * np.sin(angles[mask])
        points = np.column_stack((x, y))

        if DBSCAN and len(points) > 0:
            clusters = DBSCAN(eps=0.3, min_samples=5).fit(points)
            labels = clusters.labels_
            
            # Küme merkezlerini bul ve hareket analizi yap (Sadece en yakın hareketli küme için basitleştirilmiş)
            unique_labels = set(labels)
            if -1 in unique_labels: unique_labels.remove(-1)
            
            for label in unique_labels:
                cluster_points = points[labels == label]
                center = np.mean(cluster_points, axis=0)
                
                # Hareket Hesabı (Simülasyon: Son 5 konumdan hız)
                self.gecmis_konumlar.append(center)
                if len(self.gecmis_konumlar) > 5:
                    self.gecmis_konumlar.pop(0)
                    
                if len(self.gecmis_konumlar) >= 2:
                    dt = 0.1 # 10Hz Lidar
                    v = (self.gecmis_konumlar[-1] - self.gecmis_konumlar[0]) / (len(self.gecmis_konumlar)*dt)
                    
                    e_msg = EngelDurumu()
                    e_msg.hiz_vektoru_x = float(v[0])
                    e_msg.tahmini_konum_x = float(center[0] + v[0] * 2.0) # 2 saniye sonrası
                    self.engel_pub.publish(e_msg)
        else:
            # Scikit-learn yoksa veya puan yoksa pas geç
            pass

def main(args=None):
    rclpy.init(args=args)
    node = LidarProcessor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
