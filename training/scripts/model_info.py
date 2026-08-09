from ultralytics import YOLO
from pathlib import Path
# ===============================================================
# 文件说明：
#   查看并输出训练好的 YOLOv8 模型结构与参数信息。
# ===============================================================
# 加载训练好的模型（请将路径替换为实际模型文件）
training_dir = Path(__file__).resolve().parents[1]
model = YOLO(training_dir / "experiments" / "vehicle_detection_20250823_193130" / "weights" / "best.pt")
# 输出模型的结构与参数量信息
model.info()
