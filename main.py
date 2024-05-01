import pyautogui
import pygame
import time
import argparse
import datetime
import numpy as np
from PIL import Image, ImageDraw
import os

# Get the directory path of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize pygame for playing sounds
pygame.init()

# Global variable to keep track of modified screenshots
modified_screenshots = []
screenshot_counter = 0
detected_counter = 0

def is_pattern_present(pattern_image, screenshot):
    try:
        location = pyautogui.locate(pattern_image, screenshot)
        return location is not None
    except pyautogui.ImageNotFoundException:
        return False

def load_sounds(alert_images):
    sounds = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory path of the script
    for alert_image in alert_images:
        filename = os.path.basename(alert_image)  # Extract just the filename from the provided path
        print(f"filename {filename}")
        image_path = os.path.join(script_dir, filename)  # Construct the full path relative to the script's directory
        print(f"image_path {image_path}")
        sounds[alert_image] = image_path
    return sounds

def save_screenshot_with_timestamp(screenshot, alert_image, screenshot_logs_dir, nodisk):
    if not nodisk:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-1]
        filename = os.path.join(script_dir, screenshot_logs_dir, f"screenshot_{timestamp}_{alert_image}")
        screenshot.save(filename)
        if verbose:
            print(f"Modified screenshot saved as {filename}")
        # Add the filename to the list of modified screenshots
        modified_screenshots.append(filename)
        # Check if there are more than 10 modified screenshots, and delete the oldest one if necessary
        if len(modified_screenshots) > 10:
            os.remove(modified_screenshots.pop(0))  # Remove the oldest screenshot file

def highlight_pattern(image, location):
    overlay = np.array(image)
    border_width = 12  # Set border width to 12
    expanded_location = (
        (location.left - border_width, location.top - border_width),
        (location.left + location.width + border_width, location.top + location.height + border_width)
    )
    draw = ImageDraw.Draw(image)
    draw.rectangle(expanded_location, outline=(255, 255, 0), width=2)  # Bright yellow rectangle
    return image  # Return the modified image

def save_latest_screenshot(screenshot, screenshot_logs_dir, nodisk):
    if not nodisk:
        filename = os.path.join(script_dir, screenshot_logs_dir, "latest_screenshot.png")
        screenshot.save(filename)
        if verbose:
            print("Latest screenshot saved as latest_screenshot.png")

def main(screen_x_range, screen_y_range, alert_images, verbose, nodisk, frequency):
    global detected_counter, screenshot_counter  # Declare global variables

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
                print(f"Error deleting {file_path}: {e}")

    try:
        while True:
            detected = False
            screenshot = pyautogui.screenshot(region=(start_x, start_y, end_x - start_x, end_y - start_y))

            # Check for consecutive detections
            for alert_image in alert_images:
                if is_pattern_present(alert_image, screenshot):
                    detected = True
                    location = pyautogui.locate(alert_image, screenshot, confidence=0.99)
                    screenshot_modified = highlight_pattern(screenshot.copy(), location)
                    save_screenshot_with_timestamp(screenshot_modified, alert_image, screenshot_logs_dir, nodisk)
                
                    if detected_counter > 1:
                        sound_file = sounds[alert_image]
                        pygame.mixer.Sound(sound_file).play()
                        print(f"Pattern {alert_image} detected! Sound played.")
                        time.sleep(1.5)
                        break
                    else:
                        print(f"Pattern {alert_image} detected, below detected_counter threshold, so no sound played.")

            if detected:
                detected_counter += 1
                if verbose:
                    print(f"Detected Counter at {detected_counter} since pattern was detected.")
                if detected_counter > 20:
                    detected_counter = 5
            else:
                detected_counter = 0
                if verbose:
                    print(f"Detected Counter at {detected_counter} since pattern was not detected.")

            save_latest_screenshot(screenshot, screenshot_logs_dir, nodisk)
            time.sleep(frequency)

    except KeyboardInterrupt:
        print("\nScript stopped.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Search for patterns on the screen and play sounds when detected.")
    parser.add_argument("--screenx", type=str, default="0,1920", help="Screen region for x dimension (start,end)")
    parser.add_argument("--screeny", type=str, default="0,1080", help="Screen region for y dimension (start,end)")
    parser.add_argument("--alertimages", default="terrible.png", nargs="+", help="Filenames of alert images")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode to print additional messages")
    parser.add_argument("--nodisk", action="store_true", help="Disables storing screenshots to the disk")
    parser.add_argument("--frequency", type=float, default=0.5, help="Frequency of taking screenshots in seconds")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    verbose = args.verbose  # Store the value of verbose for later use
    nodisk = args.nodisk  # Store the value of nodisk for later use
    main(args.screenx, args.screeny, args.alertimages, args.verbose, args.nodisk, args.frequency)