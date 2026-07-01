# Changelog

All notable changes to the Starri pose-to-OSC pipeline are documented here.

## [Unreleased]

### To Do
- Confirm actual `.tflite` input/output tensor shapes by running the script once and checking console output (`INPUT DETAILS` / `OUTPUT DETAILS`)
- Confirm keypoint count/order matches `KEYPOINT_NAMES` (currently assumes COCO-17)
- Confirm whether model output is direct coordinates or heatmaps (decoder currently supports both)
- Test against `mnv1_a50_fuse3_256p_w256xh144.tflite` and `mnv1_a50_fuse5_256p_w256xh144.tflite` variants for speed/accuracy tradeoff vs the default `mnv1_fuse3`
- Verify OSC addresses/port against target SteamVR driver (currently defaults to VRChat-style port 9000)
- Install dependencies and do first live test run

## [0.1.0] - 2026-06-30

### Added
- Recreated `starri_pose_input.py` from scratch (original file was missing from disk)
- Located and confirmed three bundled TFLite pose models inside the Starri install:
  - `mnv1_a50_fuse3_256p_w256xh144.tflite` (4.4 MB)
  - `mnv1_a50_fuse5_256p_w256xh144.tflite` (2.8 MB)
  - `mnv1_fuse3_256p_w256xh144.tflite` (13.6 MB, default used in script)
- Webcam capture loop using OpenCV
- TFLite interpreter loading with input/output tensor introspection printed on startup
- Preprocessing pipeline (resize to model input dims, BGR->RGB, normalize to 0-1)
- Dual-mode keypoint decoder supporting both direct-coordinate and heatmap-style model outputs
- OSC output via `python-osc`, sending per-keypoint `/x`, `/y`, `/confidence` addresses
- Simple exponential smoothing on keypoint coordinates to reduce jitter
- Debug overlay window showing detected keypoints on the live camera feed
- ESC key listener for clean shutdown
