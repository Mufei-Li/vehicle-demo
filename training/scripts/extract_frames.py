import cv2
import os
import numpy as np
import shutil
import sys
from tqdm import tqdm
from pathlib import Path


TRAINING_DIR = Path(__file__).resolve().parents[1]


def get_user_input():
    """获取用户输入参数"""
    print("\n=== 视频帧提取工具 - 交互式界面 ===")

    # 视频路径
    while True:
        video_path = input("\n请输入视频文件路径: ").strip()
        if not os.path.exists(video_path):
            print("错误: 文件不存在，请重新输入")
        else:
            break

    # 输出目录
    # output_dir = input("\n请输入输出目录路径 (将自动创建): ").strip()
    output_dir = TRAINING_DIR / "raw_frames"
    os.makedirs(output_dir, exist_ok=True)

    # 选择提取模式
    while True:
        print("\n请选择视频提取模式:")
        print("  0: 延时摄影模式 (按帧数间隔提取)")
        print("  1: 普通视频模式 (按时间间隔提取)")
        mode_choice = input("请输入模式编号 [0/1]: ").strip()
        if mode_choice in ['0', '1']:
            mode = 'timelapse' if mode_choice == '0' else 'standard'
            break
        print("错误: 请输入0或1")

    # 获取间隔值
    interval_prompt = "\n请输入帧间隔 (整数)" if mode == 'timelapse' else "\n请输入时间间隔 (秒，支持小数)"
    while True:
        try:
            interval = input(interval_prompt + ": ").strip()
            interval_val = float(interval)
            if mode == 'timelapse':
                if interval_val < 0 or not interval_val.is_integer():
                    raise ValueError("延时模式下必须是整数≥0")
            else:
                if interval_val <= 0:
                    raise ValueError("时间间隔必须>0")
            break
        except (ValueError, TypeError) as e:
            print(f"无效输入: {e}. 请重新输入")

    # 选择分辨率
    print("\n请选择输出分辨率:")
    print("  0: 原始分辨率")
    print("  1: 720p (1280×720)")
    print("  2: 1080p (1920×1080)")
    print("  3: 4K (3840×2160)")
    while True:
        res_choice = input("请输入分辨率编号 [0-3]: ").strip()
        if res_choice in ['0', '1', '2', '3']:
            resolutions = ['original', '720p', '1080p', '4k']
            resolution = resolutions[int(res_choice)]
            break
        print("错误: 请输入0-3之间的数字")

    # 训练集比例
    while True:
        try:
            ratio_str = input("\n请输入训练集比例 (0.5-0.95, 默认0.8): ").strip()
            if not ratio_str:
                split_ratio = 0.8
                break
            ratio_val = float(ratio_str)
            if 0.5 <= ratio_val <= 0.95:
                split_ratio = ratio_val
                break
            print("比例值必须在0.5到0.95之间")
        except ValueError:
            print("无效输入，请输入小数(如0.75)或按回车使用默认值")

    return video_path, output_dir, mode, interval_val, resolution, split_ratio


def create_output_dirs(base_dir):
    """创建训练集、验证集输出目录"""
    train_dir = os.path.join(base_dir, 'train')
    val_dir = os.path.join(base_dir, 'val')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    return train_dir, val_dir


def get_target_resolution(resolution):
    """获取目标分辨率尺寸"""
    if resolution == 'original':
        return None
    resolutions = {
        '720p': (1280, 720),
        '1080p': (1920, 1080),
        '4k': (3840, 2160)
    }
    return resolutions.get(resolution, None)


def extract_frames(video_path, output_dir, mode, interval, resolution, split_ratio):
    """提取视频帧并分割数据集"""
    # 准备输出目录
    train_dir, val_dir = create_output_dirs(output_dir)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频文件 '{video_path}'")
        sys.exit(1)

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_duration = total_frames / fps

    # 计算实际间隔
    if mode == 'timelapse':
        frame_interval = max(int(interval), 1)
        total_to_extract = total_frames // frame_interval
        interval_type = "帧"
    else:
        frame_interval = max(int(interval * fps), 1)
        total_to_extract = int(total_frames / frame_interval)
        interval_type = "秒"

    # 获取目标分辨率
    target_resolution = get_target_resolution(resolution)

    # 显示摘要信息
    print("\n配置摘要:")
    print(f"  视频文件: {os.path.basename(video_path)}")
    print(f"  总帧数: {total_frames} 帧")
    print(f"  视频时长: {video_duration:.2f} 秒")
    print(f"  提取模式: {'延时摄影' if mode == 'timelapse' else '普通视频'}")
    print(f"  间隔: {interval} {interval_type}")
    print(f"  分辨率: {resolution}")
    print(f"  将提取约 {total_to_extract} 帧图像")
    print(f"  训练集比例: {split_ratio * 100:.0f}%")

    # 确认执行
    proceed = input("\n开始提取? [Y/n]: ").strip().lower()
    if proceed == 'n':
        print("操作取消")
        sys.exit()

    # 提取帧并保存
    saved_frames = []
    progress_bar = tqdm(total=total_to_extract, desc="提取视频帧", unit="帧")

    for i in range(0, total_frames, frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()

        if not ret:
            continue

        # 图像预处理
        processed = preprocess_image(frame, original_width, original_height, target_resolution)

        # 构建文件名并保存
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        filename = f"{video_name}_frame_{i:06d}.jpg"
        save_path = os.path.join(output_dir, filename)
        cv2.imwrite(save_path, processed)
        saved_frames.append(save_path)
        progress_bar.update(1)

    cap.release()
    progress_bar.close()

    # 分割训练集和验证集
    split_frames(saved_frames, train_dir, val_dir, split_ratio)

    # 最终统计
    train_count = len(os.listdir(train_dir))
    val_count = len(os.listdir(val_dir))
    print(f"\n完成! 共提取 {len(saved_frames)} 帧图像")
    print(f"  训练集: {train_dir} ({train_count} 张)")
    print(f"  验证集: {val_dir} ({val_count} 张)")
    print(f"\n下一步: 请在训练集目录中开始标注车辆")


def preprocess_image(frame, orig_width, orig_height, target_resolution):
    """图像预处理函数"""
    # 仅在有目标分辨率时调整大小
    if target_resolution:
        target_width, target_height = target_resolution

        # 保持宽高比调整大小
        scale = min(target_width / orig_width, target_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)
        resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # 创建目标尺寸的画布
        result = np.zeros((target_height, target_width, 3), dtype=np.uint8)

        # 将调整后的图像放置在画布中央
        y_offset = (target_height - new_height) // 2
        x_offset = (target_width - new_width) // 2
        result[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
    else:
        result = frame  # 保持原始尺寸

    return result


def split_frames(frame_paths, train_dir, val_dir, split_ratio):
    """分割帧到训练集和验证集"""
    np.random.shuffle(frame_paths)  # 随机打乱顺序

    split_index = int(len(frame_paths) * split_ratio)
    train_frames = frame_paths[:split_index]
    val_frames = frame_paths[split_index:]

    # 移动文件到相应目录
    print(f"\n正在分割数据集 ({split_ratio * 100:.0f}% 训练集)...")
    for path in tqdm(train_frames, desc="移动训练集图像"):
        shutil.move(path, os.path.join(train_dir, os.path.basename(path)))

    for path in tqdm(val_frames, desc="移动验证集图像"):
        shutil.move(path, os.path.join(val_dir, os.path.basename(path)))


def main():
    # 显示欢迎信息
    print("=" * 60)
    print("车辆检测项目 - 视频帧提取工具")
    print("=" * 60)
    print("此工具将帮助您：")
    print("  1. 从视频中提取帧图像")
    print("  2. 按指定分辨率调整图像尺寸")
    print("  3. 自动分割训练集和验证集")
    print("  4. 为车辆标注做好图像预处理")
    print("=" * 60)

    # 获取用户输入
    video_path, output_dir, mode, interval_val, resolution, split_ratio = get_user_input()

    # 执行提取操作
    try:
        extract_frames(
            video_path=video_path,
            output_dir=output_dir,
            mode=mode,
            interval=interval_val,
            resolution=resolution,
            split_ratio=split_ratio
        )
    except Exception as e:
        print(f"\n错误: 处理过程中发生异常 - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
