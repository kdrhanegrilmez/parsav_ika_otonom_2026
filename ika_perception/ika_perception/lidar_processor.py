import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from ika_interfaces.msg import EngelDurumu
import numpy as np
import os

try:
    from sklearn.cluster import DBSCAN
except ImportError:
    DBSCAN = None

class LidarProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')
        self.get_logger().info('Hız Vektörü Tahminli LiDAR İşleyici Başlatıldı.')
        
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.engel_pub = self.create_publisher(EngelDurumu, 'kayar_engel_durumu', 10)
        
        # Engel izleme sözlüğü {cluster_id: [history_points]}
        self.tracker = {}
        self.dt = 0.1 # 10Hz Lidar

    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)
        angles = np.linspace(msg.angle_min, msg.angle_max, len(ranges))
        
        mask = (ranges > msg.range_min) & (ranges < msg.range_max)
        points = np.column_stack((ranges[mask] * np.cos(angles[mask]), ranges[mask] * np.sin(angles[mask])))

        if DBSCAN and len(points) > 5:
            clusters = DBSCAN(eps=0.3, min_samples=5).fit(points)
            labels = clusters.labels_
            
            unique_labels = set(labels)
            if -1 in unique_labels: unique_labels.remove(-1)
            
            for label in unique_labels:
                cluster_points = points[labels == label]
                center = np.mean(cluster_points, axis=0)
                
                # Basit izleme mantığı: En yakın geçmişteki noktayı bul
                # (Yarışmada daha kompleks Kalman Filter kullanılabilir)
                found = False
                for tid in list(self.tracker.keys()):
                    history = self.tracker[tid]
                    if np.linalg.norm(center - history[-1]) < 0.5: # 0.5m yarıçapında takip
                        history.append(center)
                        if len(history) > 10: history.pop(0)
                        
                        # Hız Hesabı (Son 5 kareden)
                        if len(history) >= 5:
                            v = (history[-1] - history[-5]) / (4 * self.dt)
                            
                            e_msg = EngelDurumu()
                            e_msg.hiz_vektoru_x = float(v[0])
                            # 2 Saniye Sonrası Tahmini (Şartname 6.8 uyumu)
                            e_msg.tahmini_konum_x = float(center[0] + v[0] * 2.0)
                            self.engel_pub.publish(e_msg)
                        
                        found = True
                        break
                
                if not found:
                    self.tracker[len(self.tracker)] = [center]

def main(args=None):
    rclpy.init(args=args)
    node = LidarProcessor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
