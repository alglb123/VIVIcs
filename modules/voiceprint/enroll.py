import numpy as np
import sounddevice as sd
from resemblyzer import VoiceEncoder, preprocess_wav
from config import VOICEPRINT_TEMPLATE_PATH, AUDIO_SAMPLE_RATE
from modules import event_bus

_encoder = None


def _get_encoder() -> VoiceEncoder:
    global _encoder
    if _encoder is None:
        _encoder = VoiceEncoder()
    return _encoder


def record(seconds: int = 5) -> np.ndarray:
    audio = sd.rec(int(seconds * AUDIO_SAMPLE_RATE), samplerate=AUDIO_SAMPLE_RATE,
                   channels=1, dtype="float32")
    sd.wait()
    return audio.flatten()


def enroll(n_samples: int = 3, seconds: int = 5) -> None:
    encoder = _get_encoder()
    embeds = []
    for i in range(n_samples):
        event_bus.put({"type": "log", "msg": f"请说话（第 {i+1}/{n_samples} 段，{seconds} 秒）..."})
        wav = record(seconds)
        event_bus.put({"type": "log", "msg": f"第 {i+1} 段录制完成，处理中..."})
        wav = preprocess_wav(wav, source_sr=AUDIO_SAMPLE_RATE)
        embeds.append(encoder.embed_utterance(wav))
    template = np.mean(embeds, axis=0)
    np.save(VOICEPRINT_TEMPLATE_PATH, template)


def has_template() -> bool:
    import os
    return os.path.exists(VOICEPRINT_TEMPLATE_PATH)
