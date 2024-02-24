import ctypes
import os
import argparse
from threading import Thread, Event
import time
from pynput import keyboard
from python_imagesearch.imagesearch import imagesearch
import pyautogui
from point import Point

# === User Settings ===
VERBOSE = 't'
interval = 6
override_screen_min = None
rel_dir_path = "images"
button_offset = Point(0, 20)
# === End of Settings ===

accuracy = 0.9
script_dir = os.path.dirname(__file__)
images = [os.path.join(script_dir, rel_dir_path, img) for img in os.listdir(rel_dir_path)]

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', choices=['a', 't', 'q'], default='t', help="Set verbosity.")
parser.add_argument('-i', '--interval', metavar='float>=1', type=float, help="Set interval in seconds.")

args = parser.parse_args()
VERBOSE = args.verbose
if args.interval is not None:
    interval = args.interval if args.interval >= 1 else 1

is_enabled = Event()
is_enabled.set()
screen_min = override_screen_min or Point()
original_cursor_pos = Point()


def on_press(key):
    if key == keyboard.Key.pause:
        global is_enabled
        is_enabled.clear() if is_enabled.is_set() else is_enabled.set()


def on_release(key):
    pass


class KeyboardListener(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True  # Set as daemon thread
        self.start()

    def run(self):
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


def search():
    if VERBOSE == 'a':
        print("Searching")

    for img_path in images:
        pos = imagesearch(img_path, accuracy)

        if pos[0] != -1:
            x = pos[0] + screen_min.x
            y = pos[1] + screen_min.y

            if VERBOSE == 'a':
                print("Ad position: ", x, y)

            (original_cursor_pos.x, original_cursor_pos.y) = pyautogui.position()

            pyautogui.click(x + button_offset.x, y + button_offset.y)

            if VERBOSE == 'a' or VERBOSE == 't':
                print("Ad skipped")

            ctypes.windll.user32.SetCursorPos(original_cursor_pos.x, original_cursor_pos.y)
            break


class SearchLoop(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True  # Set as daemon thread
        self.start()

    def run(self):
        global is_enabled
        while True:
            if is_enabled.is_set():
                search()
            if VERBOSE == 'a':
                print(f"Waiting {str(interval)}s")
            time.sleep(interval)


if __name__ == "__main__":
    print(f"Running skip_ads.py at {str(interval)}s intervals in {VERBOSE} mode.")
    KeyboardListener()
    SearchLoop()
    # Keep the main thread running to allow daemon threads to continue
    while True:
        time.sleep(1)