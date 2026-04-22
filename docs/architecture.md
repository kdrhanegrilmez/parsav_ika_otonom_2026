# PARSAV İKA 2026 Teknik Mimari ve Görev Planı

Bu döküman, TEKNOFEST 2026 İnsansız Kara Aracı (İKA) yarışması için geliştirilen otonom sürüş sisteminin teknik detaylarını ve görev stratejilerini içerir.

## 1. Donanım Özellikleri
- **Kontrol Ünitesi:** NVIDIA Jetson Orin Nano (8GB RAM)
- **Alt Seviye Kontrol:** STM32 tabanlı motor sürücü kontrolcü
- **Sensörler:**
  - LiDAR: RPLiDAR S2E (30m menzil)
  - Kamera: OAK-D Pro (Stereo Depth + RGB)
  - IMU: BNO055 (9-Eksen)
  - GNSS: U-blox ZED-F9P RTK GPS

## 2. Yazılım Katmanları
### Algılama (Perception)
- **YOLOv8:** Tabela ve atış hedefi tespiti için TensorRT ile optimize edilmiştir.
- **DBSCAN:** LiDAR nokta bulutunu gerçek zamanlı kümeler ve hareketli engelleri statik olanlardan ayırır.

### Navigasyon ve Planlama
- **SLAM:** `slam_toolbox` kullanılarak parkur haritalandırması yapılır.
- **Nav2:** `SmacPlannerHybrid` algoritması ile dik eğim ve dar alanlarda optimal rota planlanır.
- **EKF:** Odom, IMU ve GPS verileri `robot_localization` ile birleştirilerek yüksek hassasiyetli konum bilgisi üretilir.

## 3. Görev Stratejileri
### Rampa ve Dik Eğim
`mission_manager`, IMU verisindeki Pitch açısını izler. Eğim 24 derecenin üzerine çıktığında Nav2 planlayıcısını duraklatır ve 2 saniye bekleme komutu gönderir.

### Kayar Engel
LiDAR işleyici, engelin hız vektörünü hesaplar. Eğer engel rotaya giriyorsa, Nav2'nin costmap katmanına geçici bir engel eklenerek aracın önceden yön değiştirmesi sağlanır.

### Atış Görevi
YOLOv8 tarafından hedeflenen merkez noktası ile aracın ekseni arasındaki fark (pixel error) PID kontrolcüye iletilerek aracın hedefe tam kilitlenmesi sağlanır.
