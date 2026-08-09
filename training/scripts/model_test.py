import os
import cv2
from ultralytics import YOLO
# ===============================================================
# 文件说明：
#   使用训练好的 YOLOv8 模型对视频进行目标检测与追踪测试。
#   可用于验证模型的实际检测效果。
# ===============================================================
# --------------------------
# 参数配置
# --------------------------
video_path = r"测试2.mp4"      # 待检测视频路径
model_path = r"best.pt"       # 模型权重文件路径
conf_threshold = 0.15         # 置信度阈值（建议 0.1~0.3）
# --------------------------
# 模型加载
# --------------------------
print("正在加载模型...")
model = YOLO(model_path)
print("模型加载完成，检测类别如下：")
print(model.names)
# --------------------------
# 打开视频文件
# --------------------------
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise FileNotFoundError(f"无法打开视频文件: {video_path}")
frame_count = 0
unique_ids = set()
total_detections = 0
empty_frame_count = 0
# --------------------------
# 主循环：逐帧检测与追踪
# --------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    if frame_count % 30 == 0:
        print(f"正在处理第 {frame_count} 帧...")
    # 使用 YOLOv8 的追踪模式（ByteTrack）
    results = model.track(
        frame,
        persist=True,
        conf=conf_threshold,
        tracker="C:/Users/mufei/miniconda3/envs/yolov8_vehicle/Lib/site-packages/ultralytics/cfg/trackers/bytetrack.yaml",
        verbose=False
    )
    if results and results[0].boxes is not None:
        boxes = results[0].boxes
        names = model.names
        if boxes.id is not None:
            ids = boxes.id.cpu().numpy().astype(int)
            classes = boxes.cls.cpu().numpy().astype(int)
            for track_id, cls in zip(ids, classes):
                name = names[int(cls)].lower()
                if any(k in name for k in ["car", "vehicle", "truck", "bus", "汽车", "卡车"]):
                    unique_ids.add(track_id)
                    x1, y1, x2, y2 = boxes.xyxy[0].int().tolist()
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{name}-{track_id}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            total_detections += len(ids)
        else:
            print(f"[帧 {frame_count}] 无追踪ID（ByteTrack未初始化）")
    else:
        empty_frame_count += 1
        print(f"[帧 {frame_count}] 无检测结果")
    # 显示检测画面
    cv2.imshow("YOLOv8 Vehicle Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

# --------------------------
# 检测结果汇总
# --------------------------
print("\n====== 检测结果汇总 ======")
print(f"视频总帧数: {frame_count}")
print(f"检测目标总数: {total_detections}")
print(f"唯一车辆ID数: {len(unique_ids)}")
print(f"无检测帧数: {empty_frame_count}")
print("==========================\n")
