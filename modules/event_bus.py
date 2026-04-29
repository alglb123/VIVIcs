import queue

_bus: queue.Queue = queue.Queue()


def put(event: dict):
    _bus.put_nowait(event)


def get_nowait() -> dict | None:
    try:
        return _bus.get_nowait()
    except queue.Empty:
        return None
