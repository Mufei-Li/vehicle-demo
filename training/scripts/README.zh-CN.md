# 训练脚本

[English version](README.md)

- `extract_frames.py`：以交互方式从视频提取帧图像到 `training/raw_frames/`；该临时目录不提交到仓库。
- `train.py`：校验 YOLO 数据集并在 `training/experiments/` 下创建新的实验记录。
- `model_test.py`：使用指定模型权重对视频进行推理测试。
- `model_info.py`：输出已记录最佳检查点的模型结构和参数信息。
- `report.py`：基于实验输出生成 HTML 分析报告。

请在仓库根目录运行脚本，例如：

```powershell
python training/scripts/train.py
```
