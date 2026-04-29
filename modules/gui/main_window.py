import customtkinter as ctk
from modules.gui.device_panel import DevicePanel
from modules.gui.log_panel import LogPanel
from modules import event_bus
from datetime import datetime


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("智能语音交互控制系统")
        self.geometry("800x520")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._build_ui()
        self._poll_events()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(1, weight=1)

        # 标题
        ctk.CTkLabel(self, text="智能语音交互控制系统", font=("", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(12, 4)
        )

        # 左侧：设备面板 + 测试按钮
        left = ctk.CTkFrame(self)
        left.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=8)
        self._device_panel = DevicePanel(left)
        self._device_panel.pack(fill="x")
        self._build_test_buttons(left)

        # 右侧：日志面板
        right = ctk.CTkFrame(self)
        right.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=8)
        ctk.CTkLabel(right, text="操作日志", font=("", 13, "bold")).pack(pady=(8, 2))
        self._log_panel = LogPanel(right)
        self._log_panel.pack(fill="both", expand=True, padx=4, pady=(0, 8))

    def _build_test_buttons(self, parent):
        ctk.CTkLabel(parent, text="快捷测试", font=("", 12)).pack(pady=(16, 4))
        from modules.control.command_dict import COMMANDS
        for cmd_text in COMMANDS:
            ctk.CTkButton(
                parent, text=cmd_text, height=28,
                command=lambda t=cmd_text: self._fire_command(t)
            ).pack(fill="x", padx=12, pady=2)

    def _fire_command(self, text: str):
        from modules.control.executor import execute
        execute(text)

    def _poll_events(self):
        while True:
            event = event_bus.get_nowait()
            if event is None:
                break
            if event["type"] == "state_change":
                self._device_panel.refresh()
            elif event["type"] == "log":
                ts = datetime.now().strftime("%H:%M:%S")
                self._log_panel.append(f"[{ts}] {event['msg']}")
        self.after(100, self._poll_events)
