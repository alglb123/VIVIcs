import customtkinter as ctk
from modules.control.device_state import DeviceState

DEVICE_LABELS = {"ac": "空调", "light": "灯光", "fan": "风扇"}
ON_COLOR = "#00e676"
OFF_COLOR = "#555555"


class DevicePanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._indicators: dict[str, ctk.CTkLabel] = {}
        ctk.CTkLabel(self, text="设备状态", font=("", 14, "bold")).pack(pady=(8, 4))
        for device, label in DEVICE_LABELS.items():
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=label, width=60).pack(side="left")
            indicator = ctk.CTkLabel(row, text="●", text_color=OFF_COLOR, font=("", 18))
            indicator.pack(side="left", padx=6)
            self._indicators[device] = indicator

    def refresh(self):
        state = DeviceState.get_all()
        for device, indicator in self._indicators.items():
            color = ON_COLOR if state.get(device) else OFF_COLOR
            indicator.configure(text_color=color)
