"""FiratBot giris noktasi (PyInstaller bunu derler).

  FiratBot.exe          -> Ayar penceresi (GUI)
  FiratBot.exe --run    -> Arka plan dongusu (runner)
"""
import sys


def main() -> None:
    if "--run" in sys.argv[1:]:
        from firatbot.runner import run_loop

        run_loop()
    else:
        from firatbot.gui import main as gui_main

        gui_main()


if __name__ == "__main__":
    main()
