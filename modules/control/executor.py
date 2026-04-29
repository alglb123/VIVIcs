from modules.control.command_dict import COMMANDS
from modules.control.device_state import DeviceState
from modules import event_bus


def execute(text: str) -> bool:
    cmd = COMMANDS.get(text.strip())
    if cmd is None:
        event_bus.put({"type": "log", "msg": f"未识别指令: {text}"})
        return False
    device, action = cmd
    DeviceState.update(device, action)
    event_bus.put({"type": "state_change", "device": device, "status": action})
    event_bus.put({"type": "log", "msg": f"执行指令: {text} → {device} {action}"})
    return True
