"""
功能：自动生成 YOLOv8 模型训练结果的 HTML 报告
主要功能：
  - 提取训练过程图像（曲线图、混淆矩阵等）
  - 读取 results.csv、val.log、results.json 等文件
  - 自动生成可视化性能报告与优化建议
"""

import os
import cv2
import glob
import argparse
import datetime
import pandas as pd


def generate_report(exp_dir):
    """生成完整的 YOLOv8 模型分析报告"""
    report_dir = os.path.join(exp_dir, "analysis_report")
    os.makedirs(report_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 收集图像与性能数据
    result_img = find_file(exp_dir, "results.png")
    cm_img = find_file(exp_dir, "confusion_matrix.png")
    labels_img = find_file(exp_dir, "labels.jpg")
    curve_images = glob.glob(os.path.join(exp_dir, "*curve*.png"))
    val_pred_imgs = glob.glob(os.path.join(exp_dir, "val_batch*pred.jpg"))
    metrics = extract_performance_metrics(exp_dir)

    # 创建报告 HTML 文件
    report_path = os.path.join(report_dir, "model_analysis_report.html")

    # HTML 样式定义
    css_style = """
    <style>
        body { font-family: 'Microsoft YaHei', sans-serif; margin: 20px; }
        h1, h2, h3 { color: #2c3e50; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }
        .image-container { text-align: center; margin-bottom: 20px; }
        .image-container img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }
        .metrics-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .metrics-table th, .metrics-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .metrics-table th { background-color: #f2f2f2; }
    </style>
    """

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>")
        f.write("<title>YOLOv8 模型分析报告</title>")
        f.write(css_style)
        f.write("</head><body><div class='container'>")
        f.write(f"<h1>YOLOv8 车辆检测模型分析报告</h1>")
        f.write(f"<p>模型路径：{exp_dir}</p><p>生成时间：{timestamp}</p>")

        # 插入关键图像（训练曲线 / 混淆矩阵等）
        for img in [result_img, cm_img, labels_img]:
            if img:
                f.write(f"<h2>{os.path.basename(img)}</h2>")
                f.write(f"<img src='{os.path.basename(img)}'><br>")
                cv2.imwrite(os.path.join(report_dir, os.path.basename(img)), cv2.imread(img))

        f.write("</div></body></html>")

    print(f"报告已生成：{report_path}")
    return report_path


def extract_performance_metrics(exp_dir):
    """提取训练性能指标"""
    metrics = {}
    csv_path = find_file(exp_dir, "results.csv")
    if csv_path:
        df = pd.read_csv(csv_path)
        last = df.iloc[-1]
        metrics["mAP50"] = last.get("metrics/mAP50(B)", None)
        metrics["precision"] = last.get("metrics/precision(B)", None)
    return metrics


def find_file(directory, filename):
    """在目录中查找指定文件"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower() == filename.lower():
                return os.path.join(root, file)
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="实验结果目录路径")
    args = parser.parse_args()
    if args.path:
        generate_report(args.path)
    else:
        print("请使用参数 --path 指定实验目录")
