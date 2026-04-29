import threading
from config import DEVICES


class DeviceState:
    _lock = threading.Lock()
    _state: dict[str, bool] = {d: False for d in DEVICES}

    @classmethod
    def update(cls, device: str, status: str) -> bool:
        if device not in cls._state:
            return False
        with cls._lock:
            cls._state[device] = (status == "on")
        return True

    @classmethod
    def get_all(cls) -> dict[str, bool]:
        with cls._lock:
            return dict(cls._state)

    @classmethod
    def get(cls, device: str) -> bool:
        with cls._lock:
            return cls._state.get(device, False)
