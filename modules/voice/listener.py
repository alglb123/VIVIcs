import threading
import numpy as np
import speech_recognition as sr
import noisereduce as nr
from modules import event_bus

_recognizer = sr.Recognizer()
_recognizer.energy_threshold = 300
_recognizer.dynamic_energy_threshold = True

_stop_event = threading.Event()
_thread: threading.Thread | None = None


def _listen_loop():
    with sr.Microphone(sample_rate=16000) as mic:
        _recognizer.adjust_for_ambient_noise(mic, duration=0.5)
        event_bus.put({"type": "log", "msg": "麦克风已就绪，开始监听..."})
        while not _stop_event.is_set():
            try:
                audio = _recognizer.listen(mic, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                continue

            # 降噪
            raw = np.frombuffer(audio.get_raw_data(convert_rate=16000, convert_width=2),
                                dtype=np.int16).astype(np.float32)
            denoised = nr.reduce_noise(y=raw, sr=16000, stationary=False)
            denoised_int = denoised.astype(np.int16)
            clean_audio = sr.AudioData(denoised_int.tobytes(), 16000, 2)

            try:
                text = _recognizer.recognize_google(clean_audio, language="zh-CN")
                event_bus.put({"type": "voice_text", "text": text})
                event_bus.put({"type": "log", "msg": f"识别结果: {text}"})
            except sr.UnknownValueError:
                event_bus.put({"type": "log", "msg": "未能识别语音，请重试"})
            except sr.RequestError as e:
                event_bus.put({"type": "log", "msg": f"网络异常: {e}"})
                break

    event_bus.put({"type": "voice_stopped"})
    event_bus.put({"type": "log", "msg": "语音监听已停止"})


def start():
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop_event.clear()
    _thread = threading.Thread(target=_listen_loop, daemon=True)
    _thread.start()


def stop():
    _stop_event.set()
