"""
starri_pose_input.py

Webcam -> Starri TFLite pose model -> OSC -> SteamVR
Recreated version. Verify tensor shapes on first run (script prints them)
and adjust KEYPOINT_NAMES / OSC address mapping if they don't match.

Requires:
    pip install opencv-python numpy python-osc tensorflow
    (tensorflow is used just for tf.lite.Interpreter; swap for
     tflite-runtime if you have it installed instead)
"""

import time
import cv2
import numpy as np
from pynput import keyboard  # optional: press ESC to quit cleanly
from pythonosc.udp_client import SimpleUDPClient

try:
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter
except ImportError:
    from tflite_runtime.interpreter import Interpreter

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
MODEL_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Starri\Starri_Data\StreamingAssets\mlModels\mnv1_fuse3_256p_w256xh144.tflite"

CAM_INDEX = 0
INPUT_W, INPUT_H = 256, 144   # matches "w256xh144" in filename

OSC_IP = "127.0.0.1"
OSC_PORT = 9000  # default VRChat OSC port; change if targeting a custom SteamVR driver

CONF_THRESHOLD = 0.25
SMOOTHING_ALPHA = 0.4  # 0 = no smoothing, 1 = frozen

# Adjust this if the model output isn't COCO-17. Run once and check
# `output_details` printout to confirm keypoint count first.
KEYPOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]

# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------
print("Loading interpreter...")
interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("=== INPUT DETAILS ===")
for d in input_details:
    print(d["name"], d["shape"], d["dtype"])
print("=== OUTPUT DETAILS ===")
for d in output_details:
    print(d["name"], d["shape"], d["dtype"])

in_shape = input_details[0]["shape"]  # e.g. [1, H, W, 3]
model_h, model_w = in_shape[1], in_shape[2]

osc_client = SimpleUDPClient(OSC_IP, OSC_PORT)
cap = cv2.VideoCapture(CAM_INDEX)

if not cap.isOpened():
    raise RuntimeError(f"Could not open webcam index {CAM_INDEX}")

smoothed = {}
running = True


def on_press(key):
    global running
    if key == keyboard.Key.esc:
        running = False
        return False


listener = keyboard.Listener(on_press=on_press)
listener.start()

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def preprocess(frame):
    img = cv2.resize(frame, (model_w, model_h))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)


def run_inference(input_tensor):
    interpreter.set_tensor(input_details[0]["index"], input_tensor)
    interpreter.invoke()
    # Assumes a single heatmap or keypoint-coords output.
    # If the model has multiple outputs (heatmap + offsets), you'll need
    # to combine them here — print output_details above to check.
    return interpreter.get_tensor(output_details[0]["index"])


def decode_keypoints(output, frame_w, frame_h):
    """
    Handles two common formats:
      - Direct coords: shape [1, N, 3] -> (y, x, score) normalized 0-1
      - Heatmaps: shape [1, H, W, N] -> take argmax per channel
    """
    points = {}
    out = np.squeeze(output)

    if out.ndim == 2 and out.shape[-1] == 3:
        # direct (y, x, score) per keypoint
        for i, name in enumerate(KEYPOINT_NAMES[: out.shape[0]]):
            y, x, score = out[i]
            if score >= CONF_THRESHOLD:
                points[name] = (float(x), float(y), float(score))

    elif out.ndim == 3:
        # heatmap [H, W, N]
        h, w, n = out.shape
        for i, name in enumerate(KEYPOINT_NAMES[:n]):
            heatmap = out[:, :, i]
            idx = np.unravel_index(np.argmax(heatmap), heatmap.shape)
            score = float(heatmap[idx])
            if score >= CONF_THRESHOLD:
                points[name] = (idx[1] / w, idx[0] / h, score)

    return points


def send_osc(points):
    for name, (x, y, score) in points.items():
        prev = smoothed.get(name, (x, y))
        sx = prev[0] * SMOOTHING_ALPHA + x * (1 - SMOOTHING_ALPHA)
        sy = prev[1] * SMOOTHING_ALPHA + y * (1 - SMOOTHING_ALPHA)
        smoothed[name] = (sx, sy)

        # Generic address scheme — rename to match your SteamVR driver's
        # expected OSC paths (e.g. VRChat avatar params use a different
        # namespace than a raw tracker driver would).
        osc_client.send_message(f"/starri/{name}/x", sx)
        osc_client.send_message(f"/starri/{name}/y", sy)
        osc_client.send_message(f"/starri/{name}/confidence", score)


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
print("Starting capture loop. Press ESC to quit.")
try:
    while running:
        ok, frame = cap.read()
        if not ok:
            continue

        frame_h, frame_w = frame.shape[:2]
        input_tensor = preprocess(frame)
        raw_output = run_inference(input_tensor)
        points = decode_keypoints(raw_output, frame_w, frame_h)
        send_osc(points)

        # Debug overlay
        for name, (x, y, score) in points.items():
            cx, cy = int(x * frame_w), int(y * frame_h)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
            cv2.putText(frame, name, (cx + 5, cy - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)

        cv2.imshow("Starri Pose -> OSC", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

        time.sleep(0.001)

finally:
    cap.release()
    cv2.destroyAllWindows()
    listener.stop()
    print("Stopped.")
