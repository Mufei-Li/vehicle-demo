import os
import torch
from ultralytics import YOLO
import sys
import datetime
import logging
from pathlib import Path


TRAINING_DIR = Path(__file__).resolve().parents[1]


def setup_logger(exp_name):
    """设置日志记录器"""
    log_dir = TRAINING_DIR / "experiments" / exp_name / "logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(exp_name)
    logger.setLevel(logging.INFO)

    # 文件处理器
    file_handler = logging.FileHandler(log_dir / "training.log")
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def main():
    # 创建唯一的实验名称（带时间戳）
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_name = f"vehicle_detection_{timestamp}"

    # 设置日志
    logger = setup_logger(exp_name)

    # 打印环境信息
    logger.info("=" * 50)
    logger.info(f"实验名称: {exp_name}")
    logger.info(f"PyTorch版本: {torch.__version__}")
    logger.info(f"CUDA可用: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        logger.info(f"GPU数量: {torch.cuda.device_count()}")
        logger.info(f"当前GPU: {torch.cuda.current_device()}")
        logger.info(f"设备名称: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.2f} GB")

        # 清理CUDA缓存
        torch.cuda.empty_cache()

    logger.info("=" * 50)

    # 数据集配置文件路径
    data_config_path = TRAINING_DIR / "dataset" / "data.yaml"
    logger.info(f"数据集配置文件路径: {data_config_path}")

    # 检查配置文件是否存在
    if not os.path.exists(data_config_path):
        logger.error(f"错误: 数据集配置文件不存在 - {data_config_path}")
        logger.info("请确保路径正确并创建dataset.yaml文件")
        return

    # 检查数据集目录
    dataset_path = TRAINING_DIR / "dataset"
    if not os.path.exists(dataset_path):
        logger.error(f"错误: 数据集目录不存在 - {dataset_path}")
        return

    # 检查训练图像目录
    train_img_path = os.path.join(dataset_path, 'images', 'train')
    if not os.path.exists(train_img_path) or len(os.listdir(train_img_path)) == 0:
        logger.error(f"错误: 训练图像目录为空或不存在 - {train_img_path}")
        return

    # 检查验证集标签目录（重要！）
    val_label_path = os.path.join(dataset_path, 'labels', 'val')
    if not os.path.exists(val_label_path) or len(os.listdir(val_label_path)) == 0:
        logger.warning(f"警告: 验证标签目录可能为空 - {val_label_path}")
        logger.info("这是之前导致评估失败的主要原因！")

    logger.info(f"找到训练图像: {len(os.listdir(train_img_path))} 张")

    # 加载模型
    logger.info("加载YOLOv8模型...")
    model = YOLO(TRAINING_DIR / "weights" / "yolov8n.pt")

    # 检测损坏的图像文件
    logger.info("检查图像完整性...")
    corrupt_files = []
    for img_name in os.listdir(train_img_path):
        if img_name.endswith(('.jpg', '.jpeg', '.png')):
            try:
                img_path = os.path.join(train_img_path, img_name)
                with open(img_path, 'rb') as f:
                    f.seek(-2, 2)
                    if f.read() != b'\xff\xd9':  # 检查JPEG结束标记
                        corrupt_files.append(img_name)
            except Exception as e:
                logger.error(f"文件检查失败: {img_name} - {e}")

    if corrupt_files:
        logger.warning(f"警告: 发现 {len(corrupt_files)} 个可能损坏的文件:")
        for file in corrupt_files[:5]:
            logger.warning(f"  - {file}")
        if len(corrupt_files) > 5:
            logger.warning(f"  ... 共 {len(corrupt_files)} 个文件")

    # 删除旧缓存文件
    cache_files = [
        os.path.join(dataset_path, 'labels', 'train.cache'),
        os.path.join(dataset_path, 'labels', 'val.cache')
    ]

    for cache_file in cache_files:
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                logger.info(f"删除旧缓存文件: {cache_file}")
            except Exception as e:
                logger.warning(f"无法删除缓存文件: {cache_file} - {e}")

    # 训练配置
    logger.info("\n训练配置:")
    train_config = {
        "data": str(data_config_path),
        "epochs": 100,
        "patience": 30,
        "imgsz": 640,
        "batch": 16 if torch.cuda.is_available() else 4,  # 根据GPU调整
        "device": '0' if torch.cuda.is_available() else 'cpu',
        "optimizer": 'AdamW',
        "lr0": 0.001,
        "cos_lr": True,
        "augment": True,
        "project": str(TRAINING_DIR / "experiments"),
        "name": exp_name,
        "exist_ok": True,
        "verbose": True,
        "rect": True,
        "save_period": 10,
        "warmup_epochs": 3.0,
        "warmup_momentum": 0.8,
        "warmup_bias_lr": 0.1,
        "weight_decay": 0.0005,
        "dropout": 0.1,
        "hsv_h": 0.015,
        "hsv_s": 0.7,
        "hsv_v": 0.4,
        "degrees": 15.0,
        "translate": 0.1,
        "scale": 0.5,
        "shear": 0.0
    }

    # 打印训练配置
    for key, value in train_config.items():
        logger.info(f"  {key}: {value}")

    # 开始训练
    logger.info("\n开始训练...")
    try:
        results = model.train(**train_config)
        logger.info("训练成功完成！")

        # 打印最终评估指标
        if results.results_dict:
            logger.info("\n训练结果摘要:")
            for metric, value in results.results_dict.items():
                logger.info(f"  {metric}: {value:.4f}")

            if "speed" in results.speed:
                logger.info("\n推理速度:")
                for name, value in results.speed.items():
                    logger.info(f"  {name}: {value:.2f}ms")

        # 保存最佳模型路径
        if os.path.exists(model.trainer.best):
            logger.info(f"\n最佳模型保存位置: {model.trainer.best}")

    except Exception as e:
        logger.error(f"训练出错: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        if exc_tb:
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(f"错误类型: {exc_type}")
            logger.error(f"文件位置: {fname}, 行号: {exc_tb.tb_lineno}")

    # 资源监控
    if torch.cuda.is_available():
        mem_used = torch.cuda.max_memory_allocated() / 1024 ** 3
        mem_total = torch.cuda.get_device_properties(0).total_memory / 1024 ** 3
        logger.info(f"\nGPU内存使用: {mem_used:.2f} / {mem_total:.2f} GB ({mem_used / mem_total:.1%})")


if __name__ == "__main__":
    main()
