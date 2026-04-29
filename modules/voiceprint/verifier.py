import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
from config import VOICEPRINT_TEMPLATE_PATH, VOICEPRINT_THRESHOLD, AUDIO_SAMPLE_RATE

_encoder = None
_template = None


def _get_encoder() -> VoiceEncoder:
    global _encoder
    if _encoder is None:
        _encoder = VoiceEncoder()
    return _encoder


def _get_template() -> np.ndarray | None:
    global _template
    if _template is None and __import__("os").path.exists(VOICEPRINT_TEMPLATE_PATH):
        _template = np.load(VOICEPRINT_TEMPLATE_PATH)
    return _template


def verify(wav: np.ndarray) -> tuple[bool, float]:
    template = _get_template()
    if template is None:
        return True, 1.0  # 未注册则放行
    wav = preprocess_wav(wav, source_sr=AUDIO_SAMPLE_RATE)
    embed = _get_encoder().embed_utterance(wav)
    score = float(np.dot(embed, template) /
                  (np.linalg.norm(embed) * np.linalg.norm(template)))
    return score >= VOICEPRINT_THRESHOLD, score
