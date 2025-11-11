# Training YOLOv12m dengan dataset lokal
# Upload folder 'dataset_extracted' ke Kaggle dulu!

from ultralytics import YOLO
import torch

# Check GPUs
num_gpus = torch.cuda.device_count()
has_cuda = torch.cuda.is_available()
print(f"CUDA available: {has_cuda}")
print(f"Available GPUs: {num_gpus}")

# Set device and batch size
if has_cuda and num_gpus >= 2:
    device = 0
    batch_size = 8
    print("Using 2 GPUs")
elif has_cuda and num_gpus == 1:
    device = 0
    batch_size = 4
    print("Using 1 GPU")
else:
    device = 'cpu'
    batch_size = 2
    print("Using CPU (slow!)")

# Load YOLOv12m
model = YOLO('yolo12m.pt')
print("Loaded YOLOv12m")

# Train - path ke dataset lokal
results = model.train(
    data='dataset_extracted/data.yaml',  # Path ke data.yaml
    epochs=150,
    imgsz=1280,
    batch=batch_size,
    name='yolo12m_parkiran',
    patience=50,
    device=device,
    workers=0,
    cache=False,
    optimizer='AdamW',
    lr0=0.001,
    lrf=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3,
    warmup_momentum=0.8,
    box=7.5,
    cls=0.5,
    dfl=1.5,
    mosaic=1.0,
    mixup=0.1,
    copy_paste=0.1,
    degrees=0.0,
    translate=0.1,
    scale=0.5,
    shear=0.0,
    perspective=0.0,
    flipud=0.0,
    fliplr=0.5,
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    max_det=300,
    amp=False,
    verbose=True
)

# Evaluate
print("\n" + "="*50)
print("VALIDATION RESULTS")
print("="*50)
metrics = model.val()
print(f"mAP50: {metrics.box.map50:.4f}")
print(f"mAP50-95: {metrics.box.map:.4f}")
print(f"Precision: {metrics.box.mp:.4f}")
print(f"Recall: {metrics.box.mr:.4f}")

# Per-class
print("\nPER-CLASS:")
for i, name in enumerate(model.names.values()):
    print(f"{name}: mAP50={metrics.box.maps[i]:.4f}, P={metrics.box.p[i]:.4f}, R={metrics.box.r[i]:.4f}")

# Test
print("\nTEST RESULTS:")
test_metrics = model.val(split='test')
print(f"mAP50: {test_metrics.box.map50:.4f}")
print(f"mAP50-95: {test_metrics.box.map:.4f}")

# Export
model.export(format='onnx')
print(f"\n✅ Model: runs/detect/yolo12m_parkiran/weights/best.pt")
