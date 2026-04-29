import threading
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from PIL import ImageFont, ImageDraw, Image
from modules import event_bus
from modules.control.command_dict import GESTURE_COMMANDS

_FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
_font = ImageFont.truetype(_FONT_PATH, 28) if os.path.exists(_FONT_PATH) else None

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../hand_landmarker.task")
_stop_event = threading.Event()
_thread: threading.Thread | None = None

# 手部骨架连接关系（21个关键点的连线对）
_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),(0,17),
]

_GESTURE_LABELS = {
    "open_palm": "手掌张开",
    "fist": "握拳",
    "victory": "比耶 V",
    "point_up": "举手 1",
}


def _fingers_up(landmarks) -> list[bool]:
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    return [landmarks[tips[i]].y < landmarks[pips[i]].y for i in range(4)]


def _classify(landmarks) -> str | None:
    up = _fingers_up(landmarks)
    count = sum(up)
    if count == 4:
        return "open_palm"
    if count == 0:
        return "fist"
    if up[0] and up[1] and not up[2] and not up[3]:
        return "victory"
    if up[0] and not up[1] and not up[2] and not up[3]:
        return "point_up"
    return None
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


def _put_chinese(frame, text: str, pos: tuple):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = _font or ImageFont.load_default()
    draw.text(pos, text, font=font, fill=(0, 255, 128))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def _draw(frame, landmarks, gesture: str | None):
    h, w = frame.shape[:2]
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in _CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (0, 255, 0), 2)
    for x, y in pts:
        cv2.circle(frame, (x, y), 4, (0, 200, 255), -1)
    if gesture:
        label = _GESTURE_LABELS.get(gesture, gesture)
        cmd = GESTURE_COMMANDS.get(gesture, "")
        frame = _put_chinese(frame, f"{label} → {cmd}", (10, 10))
    return frame


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

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 只缓存1帧，避免积压
    last_gesture = None
    win = "手势识别"
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
                frame = _draw(frame, result.hand_landmarks[0], gesture)

            if gesture and gesture != last_gesture:
                cmd = GESTURE_COMMANDS.get(gesture)
                if cmd:
                    event_bus.put({"type": "voice_text", "text": cmd})
                    event_bus.put({"type": "log", "msg": f"手势识别: {gesture} → {cmd}"})
            last_gesture = gesture

            cv2.imshow(win, frame)
            # 窗口关闭(q键或叉掉)时停止
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                _stop_event.set()
                break

    cap.release()
    cv2.destroyWindow(win)
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

