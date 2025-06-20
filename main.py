import pyautogui
import pygame
import time
import argparse
import datetime
import numpy as np
from PIL import Image, ImageDraw
import os
import mss
import pyscreeze
import tkinter as tk

# Get the directory path of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize pygame for playing sounds
pygame.init()

# Global variable to keep track of modified screenshots
modified_screenshots = []
screenshot_counter = 0
detected_counter = 0


def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-1]
    print(f"[{timestamp}] {message}")


def find_all_patterns(pattern_image, screenshot, confidence_threshold=0.99):
    try:
        locations = list(pyautogui.locateAll(pattern_image, screenshot, confidence=confidence_threshold))
        return locations  # If found, return locations
    except pyscreeze.ImageNotFoundException:
        return []  # Instead of crashing, return an empty list


def load_sounds(alert_images):
    sounds = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory path of the script
    for alert_image in alert_images:
        sounds[alert_image] = os.path.join(script_dir, "beep.wav")  # Hardcoded sound file name
    return sounds


def save_screenshot_with_timestamp(screenshot, alert_image, screenshot_logs_dir, screenshots):
    if screenshots:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-1]
        filename = os.path.join(script_dir, screenshot_logs_dir, f"screenshot_{timestamp}_{alert_image}")
        screenshot.save(filename)
        # Add the filename to the list of modified screenshots
        modified_screenshots.append(filename)
        # Check if there are more than 10 modified screenshots, and delete the oldest one if necessary
        if len(modified_screenshots) > 10:
            os.remove(modified_screenshots.pop(0))  # Remove the oldest screenshot file


def highlight_pattern(image, location):
    overlay = np.array(image)
    border_width = 8
    expanded_location = (
        (location.left - border_width, location.top - border_width),
        (location.left + location.width + border_width, location.top + location.height + border_width)
    )
    draw = ImageDraw.Draw(image)
    draw.rectangle(expanded_location, outline=(255, 255, 0), width=2)  # Bright yellow rectangle
    return image  # Return the modified image


def save_latest_screenshot(screenshot, screenshot_logs_dir, screenshots):
    if screenshots:
        filename_original = os.path.join(script_dir, screenshot_logs_dir, "latest_screenshot_original.png")
        screenshot.save(filename_original)


def select_screen_region():
    coords = {"x1": None, "y1": None, "x2": None, "y2": None}

    with mss.mss() as sct:
        monitors = sct.monitors[1:]  # skip first which is full virtual screen, use all monitors
        # Calculate bounding box that covers all monitors
        lefts = [m["left"] for m in monitors]
        tops = [m["top"] for m in monitors]
        rights = [m["left"] + m["width"] for m in monitors]
        bottoms = [m["top"] + m["height"] for m in monitors]

        virtual_left = min(lefts)
        virtual_top = min(tops)
        virtual_right = max(rights)
        virtual_bottom = max(bottoms)

        virtual_width = virtual_right - virtual_left
        virtual_height = virtual_bottom - virtual_top

    def on_mouse_down(event):
        # Convert local window coords to global screen coords
        coords["x1"] = event.x + virtual_left
        coords["y1"] = event.y + virtual_top
        canvas.delete("rect")
        canvas.create_rectangle(event.x, event.y, event.x, event.y,
                                outline="red", width=2, tag="rect")

    def on_mouse_drag(event):
        canvas.coords("rect", coords["x1"] - virtual_left, coords["y1"] - virtual_top, event.x, event.y)

    def on_mouse_up(event):
        coords["x2"] = event.x + virtual_left
        coords["y2"] = event.y + virtual_top
        root.quit()
        root.destroy()

    root = tk.Tk()
    root.overrideredirect(True)
    # Set geometry to cover the entire virtual screen across all monitors
    root.geometry(f"{virtual_width}x{virtual_height}+{virtual_left}+{virtual_top}")
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.3)
    root.configure(background='black')

    canvas = tk.Canvas(root, cursor="cross", bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    root.bind("<Escape>", lambda e: root.quit())

    root.mainloop()

    if None in (coords["x1"], coords["x2"], coords["y1"], coords["y2"]):
        return "0,0", "0,0"

    x1, x2 = sorted((coords["x1"], coords["x2"]))
    y1, y2 = sorted((coords["y1"], coords["y2"]))
    return f"{x1},{x2}", f"{y1},{y2}"


def main(screen_x_range, screen_y_range, alert_images, loglevel, screenshots, frequency, a_threshold, vt_red, vt_yellow, vt_gray, sensitivity):
    global detected_counter, screenshot_counter, screenshot_logs_dir  # Declare global variables

    # Set the default color of the terminal
    os.system("color 0F")

    # Define minimum threshold
    match_threshold = min(a_threshold, vt_red, vt_yellow, vt_gray)

    # Get the directory path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Initialize screenshot_counter
    screenshot_counter = 0

    start_x, end_x = map(int, screen_x_range.split(','))
    start_y, end_y = map(int, screen_y_range.split(','))
    screen_width, screen_height = pyautogui.size()
    start_x = max(min(start_x, screen_width - 1), 0)
    end_x = max(min(end_x, screen_width), 1)
    start_y = max(min(start_y, screen_height - 1), 0)
    end_y = max(min(end_y, screen_height), 1)

    sounds = load_sounds(alert_images)

    # Create screenshot_logs directory if it doesn't exist
    screenshot_logs_dir = os.path.join(script_dir, "screenshot_logs")
    if not os.path.exists(screenshot_logs_dir):
        os.makedirs(screenshot_logs_dir)
    else:
        # Clear the contents of screenshot_logs directory
        for filename in os.listdir(screenshot_logs_dir):
            file_path = os.path.join(screenshot_logs_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                log_message(f"Error deleting {file_path}: {e}")

    try:
        with mss.mss() as sct:
            for monitor_num, monitor in enumerate(sct.monitors, 1):
                # Calculate start and end coordinates for each monitor
                start_x, end_x = map(int, screen_x_range.split(','))
                start_y, end_y = map(int, screen_y_range.split(','))
                
                # Adjust start and end coordinates based on monitor's position
                monitor_start_x, monitor_start_y = monitor["left"], monitor["top"]
                monitor_end_x = monitor_start_x + monitor["width"]
                monitor_end_y = monitor_start_y + monitor["height"]

                # Ensure coordinates are within monitor bounds
                start_x = max(min(start_x, monitor_end_x - 1), monitor_start_x)
                end_x = max(min(end_x, monitor_end_x), monitor_start_x + 1)
                start_y = max(min(start_y, monitor_end_y - 1), monitor_start_y)
                end_y = max(min(end_y, monitor_end_y), monitor_start_y + 1)

                log_message(f"Capturing screenshots from monitor {monitor_num} - X: {start_x}-{end_x}, Y: {start_y}-{end_y}")

                while True:
                    detected = False

                    # Capture screenshot
                    screenshot = sct.grab({"top": start_y, "left": start_x, "width": end_x - start_x, "height": end_y - start_y})

                    # Convert screenshot to PIL Image
                    screenshot = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                    # Check for consecutive detections
                    num_matches = 0
                    for alert_image in alert_images:
                        locations = find_all_patterns(alert_image, screenshot)
                        for location in locations:
                            detected = True
                            num_matches += 1
                            screenshot_modified = highlight_pattern(screenshot.copy(), location)
                            save_screenshot_with_timestamp(screenshot_modified, alert_image, screenshot_logs_dir, screenshots)
                            if loglevel >= 2:
                                log_message(f"DEBUG - Pattern {alert_image} detected!")

                    if detected:
                        detected_counter += 1
                        if loglevel >= 2:
                            if detected_counter >= 20:
                                detected_counter = 19
                                log_message(f"DEBUG - Detected Counter at 20+ since pattern was detected.")
                            else:
                                log_message(f"DEBUG - Detected Counter at {detected_counter} since pattern was detected.")
                    else:
                        detected_counter = 0
                        if loglevel >= 2:
                            log_message(f"DEBUG - Detected Counter at {detected_counter} since pattern was not detected.")

                    if detected_counter > sensitivity:
                        if num_matches >= match_threshold:
                            if num_matches >= a_threshold:
                                sound_file = sounds[alert_image]
                                pygame.mixer.Sound(sound_file).play()
                            if num_matches >= vt_red:
                                os.system("color C0")
                                time.sleep(0.25)
                                os.system("color 0F")
                                time.sleep(0.25)
                                os.system("color C0")
                            elif num_matches >= vt_yellow:
                                os.system("color E0")
                                time.sleep(0.25)
                                os.system("color 0F")
                                time.sleep(0.25)
                                os.system("color E0")
                            elif num_matches >= vt_gray:
                                os.system("color 80")
                                time.sleep(0.25)
                                os.system("color 0F")
                                time.sleep(0.25)
                                os.system("color 80")
                            if loglevel >= 1:
                                log_message(f"INFO - Alerted - Detected {num_matches} time(s), at or above Match Threshold: {match_threshold}.")
                            time.sleep(frequency)
                            os.system("color 0F")
                            time.sleep(0.5)
                        elif num_matches > 0:
                            if loglevel >= 2:
                                log_message(f"DEBUG - No Alert - Detected {num_matches} time(s), but below Match Threshold: {match_threshold}.")

                    save_latest_screenshot(screenshot, screenshot_logs_dir, screenshots)
                    time.sleep(frequency)

    except KeyboardInterrupt:
        log_message("\nWARNING - Script stopped.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Search for patterns on the screen and play sounds when detected.")
    parser.add_argument("--screenx", type=str, default="0,0", help="Screen region for x dimension (start,end)")
    parser.add_argument("--screeny", type=str, default="0,0", help="Screen region for y dimension (start,end)")
    parser.add_argument("--alertimages", default="terrible.png", nargs="+", help="Filenames of alert images")
    parser.add_argument("--loglevel", type=int, default=1, help="Level of Logging: '0' for none, '1' for standard (default), '2' for verbose")
    parser.add_argument("--screenshots", action="store_true", help="Enables storing screenshots to the disk")
    parser.add_argument("--frequency", type=float, default=0.5, help="Frequency of taking screenshots in seconds")
    parser.add_argument("--a_threshold", type=int, default=1, help="Number of matches required to trigger audible alert ('0' disables the alert)")
    parser.add_argument("--vt_red", type=int, default=0, help="Number of matches required to trigger visual alert ('0' disables the alert)")
    parser.add_argument("--vt_yellow", type=int, default=1, help="Number of matches required to trigger visual alert ('0' disables the alert)")
    parser.add_argument("--vt_gray", type=int, default=0, help="Number of matches required to trigger visual alert ('0' disables the alert)")
    parser.add_argument("--sensitivity", type=int, default=2, help="Larger value helps filter out false positives")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    frequency = args.frequency
    a_threshold = args.a_threshold
    vt_red = args.vt_red
    vt_yellow = args.vt_yellow
    vt_gray = args.vt_gray
    screenx = args.screenx
    screeny = args.screeny

    if frequency <= 0.5: frequency = 0.5
    if a_threshold <= 0: a_threshold = 9999
    if vt_red <= 0: vt_red = 9999
    if vt_yellow <= 0: vt_yellow = 9999
    if vt_gray <= 0: vt_gray = 9999

    if screenx == "0,0" or screeny == "0,0":
        log_message("Both X and Y coordinates were not provided — launching box selector...")
        screenx, screeny = select_screen_region()
        log_message(f"Selected region - X: {screenx}, Y: {screeny}")

    main(screenx, screeny, args.alertimages, args.loglevel, args.screenshots,
         frequency, a_threshold, vt_red, vt_yellow, vt_gray, args.sensitivity)
