#!/usr/bin/env python3
from ultralytics import YOLO
import sys

def main():
    try:
        # YOLOv8n modelini yükle
        model = YOLO('yolov8n.pt') 
        
        print("TensorRT dönüşümü başlatılıyor (bu işlem Jetson üzerinde uzun sürebilir)...")
        
        # TensorRT engine olarak export et
        # device=0 (GPU), half=True (FP16), workspace=4 (4GB RAM kullanımı)
        model.export(format='engine', device=0, half=True, workspace=4) 
        
        print("Model başarıyla 'yolov8n.engine' olarak kaydedildi.")
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == '__main__':
    main()
