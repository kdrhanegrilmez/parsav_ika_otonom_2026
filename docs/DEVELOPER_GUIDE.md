# PARSAV İKA - Teknik Geliştirici Kılavuzu (Nisan 2026)

Bu doküman, KARABÜK GM PARSAV İKA takımının otonom sürüş yazılımını geliştirmek, test etmek ve sahaya sürmek için gereken tüm teknik detayları içerir.

## 🏗️ Sistem Mimarisi
Sistem **ROS 2 Jazzy** ve **Gazebo Sim (Harmonic)** üzerine inşa edilmiştir.

### Kritik Bileşenler:
*   **Mission Manager (FSM v3.0):** Aracın karar mekanizmasıdır. `/mission_start` sinyaliyle "Oto-Pilot" moduna geçer ve önceden tanımlanmış waypointleri sırasıyla takip eder.
*   **Nav2 Stack:** `SmacPlannerHybrid` algoritması ile karmaşık parkurda (rampa, dar geçişler) rota planlar.
*   **YOLO Perception:** `ultralytics` tabanlı tabela ve hedef algılayıcı. TensorRT (.engine) desteği mevcuttur.
*   **Watchdog:** Sistem sağlığını 200ms aralıklarla denetler. Kalp atışı kesilirse aracı anında durdurur.

## 🚀 Çalıştırma Talimatları (WSL / Ubuntu 24.04)

### 1. Derleme
Herhangi bir kod değişikliğinden sonra mutlaka derleme yapın:
```bash
cd /mnt/c/Users/kadir/Desktop/teknofestOtonomSurus/codes/ika_ws
colcon build --symlink-install
source install/setup.bash
```

### 2. Simülasyonu Başlatma
```bash
ros2 launch ika_bringup ika.launch.py
```

### 3. Otonom Sürüşü Tetikleme
Sistem açıldıktan ve Gazebo'da **Play** butonuna basıldıktan sonra:
```bash
ros2 topic pub /mission_start std_msgs/msg/Bool "{data: true}" -1
```

## ⚠️ Bilinen Sorunlar ve Çözümleri

### NumPy / ndarrayobject.h Hatası
`ika_interfaces` derlenirken bu hata alınırsa şu komutu çalıştırın (bugün çözüldü):
```bash
sudo ln -s /usr/lib/python3-dist-packages/numpy/core/include/numpy /usr/include/numpy
```

### Beyaz Ekran (Model Görünmeme)
Eğer modeller renksiz görünürse, Launch dosyasındaki `GZ_SIM_RESOURCE_PATH` değişkeninin `codes/ika_ws/src/ika_gazebo/models` yolunu gösterdiğinden emin olun.

## 📂 Dosya Yapısı
*   `src/requirements.txt`: Python bağımlılıkları.
*   `src/docs/architecture.md`: Üst seviye mimari diyagramı.
*   `src/ika_mission_manager/mission_manager.py`: Oto-pilot koordinatları buradadır.
