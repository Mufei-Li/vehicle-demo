# Dataset Notes

## Composition

- 399 labelled vehicle images, split into training and validation sets.
- 308 corresponding YOLO-format label files.
- One class: `vehicle`.

## Provenance and preparation

Images were extracted from project video material and manually prepared for YOLO training. The repository retains the labelled dataset used by the recorded experiment. The earlier unlabelled-frame staging directory is intentionally excluded because it duplicates the final dataset images.

## Reproducibility

The dataset configuration is at `training/dataset/data.yaml`. Training code is at `training/scripts/train.py`, and the associated configuration, metrics, charts, and checkpoints are kept with the experiment record.
