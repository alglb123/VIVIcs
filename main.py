import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="webrtcvad")

from modules.gui.main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
