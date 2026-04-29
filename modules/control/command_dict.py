# 语音指令 → (设备, 动作) 映射
COMMANDS: dict[str, tuple[str, str]] = {
    "打开空调": ("ac", "on"),
    "关闭空调": ("ac", "off"),
    "打开灯光": ("light", "on"),
    "关闭灯光": ("light", "off"),
    "打开风扇": ("fan", "on"),
    "关闭风扇": ("fan", "off"),
}

# 手势 → 指令映射
GESTURE_COMMANDS: dict[str, str] = {
    "open_palm": "打开灯光",
    "fist": "关闭灯光",
    "victory": "打开空调",
    "point_up": "关闭空调",
}
