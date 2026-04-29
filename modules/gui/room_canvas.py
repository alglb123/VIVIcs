import tkinter as tk
import customtkinter as ctk
from modules.control.device_state import DeviceState

# 设备在画布上的位置和图标配置
_DEVICES = {
    "light": {"label": "灯光", "x": 200, "y": 120, "icon": "💡"},
    "ac":    {"label": "空调", "x": 340, "y": 80,  "icon": "❄"},
    "fan":   {"label": "风扇", "x": 200, "y": 240, "icon": "🌀"},
}
ON_FILL  = "#00e676"
OFF_FILL = "#444444"
GLOW     = "#b9ffd8"


class RoomCanvas(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text="房间仿真视图", font=("", 13, "bold")).pack(pady=(6, 2))
        self._canvas = tk.Canvas(self, bg="#1a1a2e", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self._canvas.bind("<Configure>", lambda _: self.refresh())
        self._items: dict[str, dict] = {}

    def _draw_room(self, w, h):
        c = self._canvas
        c.delete("all")
        # 房间轮廓
        c.create_rectangle(20, 20, w - 20, h - 20,
                            outline="#4a4a8a", width=2, fill="#16213e")
        c.create_text(w // 2, 12, text="智能家居 · 客厅", fill="#6a6aaa", font=("", 9))

        state = DeviceState.get_all()
        self._items.clear()
        for dev, cfg in _DEVICES.items():
            on = state.get(dev, False)
            # 坐标按画布尺寸等比缩放
            x = int(cfg["x"] / 400 * w)
            y = int(cfg["y"] / 320 * h)
            # 发光晕圈（仅 on 状态）
            if on:
                c.create_oval(x - 28, y - 28, x + 28, y + 28,
                              fill=GLOW, outline="", stipple="gray50")
            # 设备圆形底座
            fill = ON_FILL if on else OFF_FILL
            c.create_oval(x - 18, y - 18, x + 18, y + 18,
                          fill=fill, outline="#888", width=1)
            # 图标文字
            c.create_text(x, y, text=cfg["icon"], font=("", 14))
            # 标签
            status = "ON" if on else "OFF"
            c.create_text(x, y + 28, text=f"{cfg['label']} {status}",
                          fill="#cccccc", font=("", 8))
            self._items[dev] = {"x": x, "y": y}

    def refresh(self):
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w > 1 and h > 1:
            self._draw_room(w, h)
