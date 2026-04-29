import customtkinter as ctk
from modules.gui.device_panel import DevicePanel
from modules.gui.log_panel import LogPanel
from modules.gui.room_canvas import RoomCanvas
from modules import event_bus
from modules.voice import listener as voice_listener
from modules.gesture import detector as gesture_detector
from datetime import datetime


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("智能语音交互控制系统")
        self.geometry("1050x560")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._listening = False
        self._gesturing = False
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
        # 麦克风按钮
        self._mic_btn = ctk.CTkButton(
            parent, text="🎤 开始监听", height=36, fg_color="#1565c0",
            hover_color="#1976d2", command=self._toggle_voice
        )
        self._mic_btn.pack(fill="x", padx=10, pady=(14, 3))
        # 手势按钮
        self._gesture_btn = ctk.CTkButton(
            parent, text="✋ 开始手势", height=36, fg_color="#2e7d32",
            hover_color="#388e3c", command=self._toggle_gesture
        )
        self._gesture_btn.pack(fill="x", padx=10, pady=(3, 6))

        ctk.CTkLabel(parent, text="指令控制", font=("", 12)).pack(pady=(6, 4))
        from modules.control.command_dict import COMMANDS
        for cmd_text in COMMANDS:
            ctk.CTkButton(
                parent, text=cmd_text, height=28,
                command=lambda t=cmd_text: self._fire(t)
            ).pack(fill="x", padx=10, pady=2)

    def _toggle_gesture(self):
        if not self._gesturing:
            self._gesturing = True
            self._gesture_btn.configure(
                text="⏹ 停止手势", fg_color="#b71c1c", hover_color="#c62828"
            )
            gesture_detector.start()
        else:
            self._gesturing = False
            self._gesture_btn.configure(
                text="✋ 开始手势", fg_color="#2e7d32", hover_color="#388e3c"
            )
            gesture_detector.stop()

    def _toggle_voice(self):
        if not self._listening:
            self._listening = True
            self._mic_btn.configure(
                text="⏹ 停止监听", fg_color="#b71c1c", hover_color="#c62828"
            )
            voice_listener.start()
        else:
            self._listening = False
            self._mic_btn.configure(
                text="🎤 开始监听", fg_color="#1565c0", hover_color="#1976d2"
            )
            voice_listener.stop()

    def _fire(self, text: str):
        from modules.control.executor import execute
        execute(text)

    def _poll_events(self):
        while True:
            event = event_bus.get_nowait()
            if event is None:
                break
            t = event["type"]
            if t == "state_change":
                self._device_panel.refresh()
                self._room.refresh()
            elif t == "log":
                ts = datetime.now().strftime("%H:%M:%S")
                self._log_panel.append(f"[{ts}] {event['msg']}")
            elif t == "voice_text":
                from modules.control.executor import execute
                execute(event["text"])
            elif t == "voice_stopped":
                self._listening = False
                self._mic_btn.configure(
                    text="🎤 开始监听", fg_color="#1565c0", hover_color="#1976d2"
                )
            elif t == "gesture_stopped":
                self._gesturing = False
                self._gesture_btn.configure(
                    text="✋ 开始手势", fg_color="#2e7d32", hover_color="#388e3c"
                )
        self.after(100, self._poll_events)
