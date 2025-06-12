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

def save_screenshot_with_timestamp(screenshot, alert_image, screenshot_logs_dir, nodisk):
    if not nodisk:
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

def save_latest_screenshot(screenshot, screenshot_logs_dir, nodisk):
    if not nodisk:
        filename_original = os.path.join(script_dir, screenshot_logs_dir, "latest_screenshot_original.png")
        screenshot.save(filename_original)

def main(screen_x_range, screen_y_range, alert_images, loglevel, nodisk, frequency, a_threshold, v_threshold, sensitivity):
    global detected_counter, screenshot_counter, screenshot_logs_dir  # Declare global variables

    # Set the default color of the terminal
    os.system("color 0F")

    # Define minimum threshold
    match_threshold = min(a_threshold, v_threshold)

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
                            save_screenshot_with_timestamp(screenshot_modified, alert_image, screenshot_logs_dir, nodisk)
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
                            if num_matches >= v_threshold:
                                os.system("color E0")
                            if loglevel >= 1:
                                log_message(f"INFO - Alerted - Detected {num_matches} time(s), at or above Match Threshold: {match_threshold}.")
                            time.sleep(frequency)
                            os.system("color 0F")
                            time.sleep(1)
                        elif num_matches > 0:
                            if loglevel >= 2:
                                log_message(f"DEBUG - No Alert - Detected {num_matches} time(s), but below Match Threshold: {match_threshold}.")

                    save_latest_screenshot(screenshot, screenshot_logs_dir, nodisk)
                    time.sleep(frequency)

    except KeyboardInterrupt:
        log_message("\nWARNING - Script stopped.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Search for patterns on the screen and play sounds when detected.")
    parser.add_argument("--screenx", type=str, default="0,1920", help="Screen region for x dimension (start,end)")
    parser.add_argument("--screeny", type=str, default="0,1080", help="Screen region for y dimension (start,end)")
    parser.add_argument("--alertimages", default="terrible.png", nargs="+", help="Filenames of alert images")
    parser.add_argument("--loglevel", type=int, default=1, help="Level of Logging: '0' for none, '1' for standard (default), '2' for verbose")
    parser.add_argument("--nodisk", action="store_true", help="Disables storing screenshots to the disk")
    parser.add_argument("--frequency", type=float, default=0.5, help="Frequency of taking screenshots in seconds")
    parser.add_argument("--a_threshold", type=int, default=1, help="Number of matches required to trigger audible alert ('0' disables the alert)")
    parser.add_argument("--v_threshold", type=int, default=1, help="Number of matches required to trigger visual alert ('0' disables the alert)")
    parser.add_argument("--sensitivity", type=int, default=2, help="Larger value helps filter out false positives")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    a_threshold = args.a_threshold
    v_threshold = args.v_threshold
    if a_threshold <= 0: a_threshold = 9999
    if v_threshold <= 0: v_threshold = 9999
    main(args.screenx, args.screeny, args.alertimages, args.loglevel, args.nodisk, args.frequency, a_threshold, v_threshold, args.sensitivity)