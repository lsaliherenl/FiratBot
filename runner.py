"""Yerel/dev giris noktasi: dongu calistirir (firatbot.runner.run_loop).

Paketlenmis surumde app.py --run kullanilir; bu dosya gelistirme ve mevcut
Startup kisayolu (pythonw runner.py) icin korunur.
"""
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
os.chdir(_here)
sys.path.insert(0, _here)

from firatbot.runner import run_loop  # noqa: E402

if __name__ == "__main__":
    run_loop()
