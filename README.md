# Starri Pose -> OSC

Headsetless VR motion tracking: webcam -> Starri's bundled TFLite pose model -> OSC -> SteamVR.

## What this does

Starri (the Steam game) ships with lightweight MobileNetV1-based pose estimation
models. This script pulls one of those models out of the game's install folder,
runs it against a webcam feed, and streams the detected body keypoints out over
OSC so they can drive SteamVR trackers (or VRChat avatar params) without a
headset's built-in tracking.

## Requirements

```bash
pip install opencv-python numpy python-osc pynput tensorflow
```

Or via a `requirements.txt`:

```
opencv-python
numpy
python-osc
pynput
tensorflow
```

(`tensorflow` is only used for `tf.lite.Interpreter`. If you'd rather not pull
in full TF, swap to `tflite-runtime` instead — the script will use whichever
is installed.)

## Model files

Located at:

```
C:\Program Files (x86)\Steam\steamapps\common\Starri\Starri_Data\StreamingAssets\mlModels\
```

Three variants are bundled:

| File | Size | Notes |
|---|---|---|
| `mnv1_fuse3_256p_w256xh144.tflite` | 13.6 MB | Default used in the script; largest, likely most accurate |
| `mnv1_a50_fuse3_256p_w256xh144.tflite` | 4.4 MB | Smaller/faster variant |
| `mnv1_a50_fuse5_256p_w256xh144.tflite` | 2.8 MB | Smallest/fastest variant |

Swap `MODEL_PATH` in the script to try the other two if you need more speed at
the cost of accuracy.

## Usage

```bash
python starri_pose_input.py
```

On first run, check the console for `INPUT DETAILS` / `OUTPUT DETAILS` —
this confirms the model's real tensor shapes and keypoint format (the script
assumes COCO-17 style keypoints and supports both direct-coordinate and
heatmap-style outputs, but you should verify against what's actually printed).

A debug window will show the webcam feed with detected keypoints overlaid.
Press `ESC` to quit.

## OSC output

Sends to `127.0.0.1:9000` by default (VRChat's typical OSC input port) using
per-keypoint addresses:

```
/starri/<keypoint_name>/x
/starri/<keypoint_name>/y
/starri/<keypoint_name>/confidence
```

Change `OSC_IP` / `OSC_PORT` in the script if you're targeting a custom
SteamVR driver instead of VRChat.

## Known gaps / to verify

- Exact keypoint order and count haven't been confirmed against the live
  model output yet (see `KEYPOINT_NAMES` in the script)
- Whether the model outputs heatmaps or direct coordinates isn't confirmed
- OSC address scheme is generic and may need remapping to match whatever
  driver/avatar setup is receiving it
- No calibration step yet (raw normalized 0-1 coords, no scaling to
  real-world tracker space)

See `changelog.md` for version history.
