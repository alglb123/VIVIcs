import customtkinter as ctk
from config import LOG_MAX_LINES


class LogPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._text = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self._text.pack(fill="both", expand=True, padx=4, pady=4)
        self._count = 0

    def append(self, msg: str):
        self._text.configure(state="normal")
        if self._count >= LOG_MAX_LINES:
            self._text.delete("1.0", "2.0")
        else:
            self._count += 1
        self._text.insert("end", msg + "\n")
        self._text.see("end")
        self._text.configure(state="disabled")
