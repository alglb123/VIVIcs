import threading
import os
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from modules import event_bus
from modules.control.command_dict import GESTURE_COMMANDS

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../hand_landmarker.task")
_stop_event = threading.Event()
_thread: threading.Thread | None = None


def _fingers_up(landmarks) -> list[bool]:
    tips = [4, 8, 12, 16, 20]
    pips = [3, 6, 10, 14, 18]
    up = [landmarks[tips[0]].x < landmarks[pips[0]].x]
    for i in range(1, 5):
        up.append(landmarks[tips[i]].y < landmarks[pips[i]].y)
    return up


def _classify(landmarks) -> str | None:
    up = _fingers_up(landmarks)
    count = sum(up[1:])
    if count == 5 or (up[0] and count == 4):
        return "open_palm"
    if count == 0:
        return "fist"
    if up[1] and up[2] and not up[3] and not up[4]:
        return "victory"
    if up[1] and not up[2] and not up[3] and not up[4]:
        return "point_up"
    return None


def _detect_loop():
    base_options = mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.6,
    )
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        event_bus.put({"type": "log", "msg": "摄像头不可用"})
        event_bus.put({"type": "gesture_stopped"})
        return

    last_gesture = None
    event_bus.put({"type": "log", "msg": "手势识别已启动"})
    with vision.HandLandmarker.create_from_options(options) as landmarker:
        while not _stop_event.is_set():
            ok, frame = cap.read()
            if not ok:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = landmarker.detect(mp_image)
            gesture = None
            if result.hand_landmarks:
                gesture = _classify(result.hand_landmarks[0])
            if gesture and gesture != last_gesture:
                cmd = GESTURE_COMMANDS.get(gesture)
                if cmd:
                    event_bus.put({"type": "voice_text", "text": cmd})
                    event_bus.put({"type": "log", "msg": f"手势识别: {gesture} → {cmd}"})
            last_gesture = gesture

    cap.release()
    event_bus.put({"type": "gesture_stopped"})
    event_bus.put({"type": "log", "msg": "手势识别已停止"})


def start():
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop_event.clear()
    _thread = threading.Thread(target=_detect_loop, daemon=True)
    _thread.start()


def stop():
    _stop_event.set()

