import customtkinter as ctk
from modules.gui.device_panel import DevicePanel
from modules.gui.log_panel import LogPanel
from modules.gui.room_canvas import RoomCanvas
from modules import event_bus
from datetime import datetime


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("智能语音交互控制系统")
        self.geometry("1050x560")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._build_ui()
        self._poll_events()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="智能语音交互控制系统", font=("", 18, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(12, 4)
        )

        # 左栏：设备状态 + 指令按钮
        left = ctk.CTkFrame(self, width=160)
        left.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=8)
        left.pack_propagate(False)
        self._device_panel = DevicePanel(left)
        self._device_panel.pack(fill="x")
        self._build_buttons(left)

        # 中栏：Canvas 仿真建模
        self._room = RoomCanvas(self)
        self._room.grid(row=1, column=1, sticky="nsew", padx=4, pady=8)

        # 右栏：日志
        right = ctk.CTkFrame(self)
        right.grid(row=1, column=2, sticky="nsew", padx=(4, 8), pady=8)
        ctk.CTkLabel(right, text="操作日志", font=("", 13, "bold")).pack(pady=(8, 2))
        self._log_panel = LogPanel(right)
        self._log_panel.pack(fill="both", expand=True, padx=4, pady=(0, 8))

    def _build_buttons(self, parent):
        ctk.CTkLabel(parent, text="指令控制", font=("", 12)).pack(pady=(14, 4))
        from modules.control.command_dict import COMMANDS
        for cmd_text in COMMANDS:
            ctk.CTkButton(
                parent, text=cmd_text, height=28,
                command=lambda t=cmd_text: self._fire(t)
            ).pack(fill="x", padx=10, pady=2)

    def _fire(self, text: str):
        from modules.control.executor import execute
        execute(text)

    def _poll_events(self):
        while True:
            event = event_bus.get_nowait()
            if event is None:
                break
            if event["type"] == "state_change":
                self._device_panel.refresh()
                self._room.refresh()
            elif event["type"] == "log":
                ts = datetime.now().strftime("%H:%M:%S")
                self._log_panel.append(f"[{ts}] {event['msg']}")
        self.after(100, self._poll_events)
