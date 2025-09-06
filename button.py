#!/usr/bin/env python3
from gpiozero import Button
from datetime import datetime
from pathlib import Path
from threading import Lock
import sys

from picamera2 import Picamera2

# --- Settings ---
GPIO_PIN = 17              # button on GPIO17 -> GND
PULL_UP = True             # True if button -> GND, False if button -> 3V3
SAVE_DIR = Path.home() / "Desktop"
# ----------------

SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Init camera (headless: no preview)
picam2 = Picamera2()

# Use a still configuration (max native resolution by default)
# You can force a size with: picam2.create_still_configuration(main={"size": (2304, 1296)})
config = picam2.create_still_configuration()
picam2.configure(config)

# Start the camera
picam2.start()

# Try to enable autofocus if the camera supports it (e.g., Camera Module 3)
try:
    picam2.set_controls({"AfMode": 2})  # 2 = Continuous autofocus
except Exception:
    pass  # Older fixed-focus modules just ignore this

lock = Lock()

def capture_still():
    if not lock.acquire(blocking=False):
        # ignore if a capture is already in progress
        return
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        outfile = SAVE_DIR / f"rpicam_{ts}.jpg"
        print(f"[BTN] pressed -> capturing {outfile}")
        picam2.capture_file(str(outfile))
        print("[OK] saved:", outfile)
    except Exception as e:
        print("[ERR] capture failed:", e, file=sys.stderr)
    finally:
        lock.release()

# Button setup with debounce
button = Button(GPIO_PIN, pull_up=PULL_UP, bounce_time=0.05)
button.when_pressed = capture_still

print("Ready. Press the button on GPIO17 to take a photo. Ctrl+C to exit.")
try:
    import signal; signal.pause()
except KeyboardInterrupt:
    pass
finally:
    picam2.stop()
