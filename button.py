#!/usr/bin/env python3
from gpiozero import Button
from subprocess import run, CalledProcessError
from datetime import datetime
from pathlib import Path
import os

# Button on GPIO17, using internal pull-up (active when pressed to GND)
button = Button(17, pull_up=True, bounce_time=0.05)

# Save to Desktop of current user
desktop = Path.home() / "Desktop"
desktop.mkdir(parents=True, exist_ok=True)

def take_photo():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = desktop / f"webcam_{ts}.jpg"
    print(f"[INFO] Button pressed → capturing to {outfile}")

    # Capture with fswebcam (adjust --device /dev/video0 if needed)
    cmd = [
        "fswebcam",
        "--no-banner",          # remove timestamp banner
        "--resolution", "1920x1080",  # change if your cam needs another size
        str(outfile)
    ]
    try:
        run(cmd, check=True)
        print("[OK] Saved:", outfile)
    except FileNotFoundError:
        print("ERROR: fswebcam not found. Install with: sudo apt install fswebcam")
    except CalledProcessError as e:
        print("ERROR: fswebcam failed:", e)

print("[READY] Press the button on GPIO17 to take a photo. Ctrl+C to exit.")
button.when_pressed = take_photo

# Keep script running
try:
    import signal; signal.pause()
except KeyboardInterrupt:
    pass
