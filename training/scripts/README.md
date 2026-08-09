# Training Scripts

[中文版本](README.zh-CN.md)

- `extract_frames.py`: interactively extracts frames from a video into `training/raw_frames/`; this temporary staging directory is not committed.
- `train.py`: validates the YOLO dataset and starts a new experiment under `training/experiments/`.
- `model_test.py`: runs video inference with a specified model weight.
- `model_info.py`: prints model structure and parameter information for the recorded best checkpoint.
- `report.py`: generates an HTML analysis report from experiment outputs.

Run scripts from the repository root, for example:

```powershell
python training/scripts/train.py
```
