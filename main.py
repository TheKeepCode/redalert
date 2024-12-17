import pyautogui
import pygame
import time
import argparse
import datetime
import numpy as np
from PIL import Image, ImageDraw
import os
import mss
import pytesseract

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

def is_pattern_present(pattern_image, screenshot):
    try:
        location = pyautogui.locate(pattern_image, screenshot, confidence=0.99)
        return location  # Return the location object directly
    except pyautogui.ImageNotFoundException:
        return None

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
    border_width = 12  # Set border width to 12
    expanded_location = (
        (location.left - border_width, location.top - border_width),
        (location.left + location.width + border_width, location.top + location.height + border_width)
    )
    draw = ImageDraw.Draw(image)
    draw.rectangle(expanded_location, outline=(255, 255, 0), width=2)  # Bright yellow rectangle
    return image  # Return the modified image

def save_latest_screenshot(screenshot, screenshot_logs_dir, nodisk, ocr):
    if not nodisk:
        filename_original = os.path.join(script_dir, screenshot_logs_dir, "latest_screenshot_original.png")
        filename_preprocessed = os.path.join(script_dir, screenshot_logs_dir, "latest_screenshot_preprocessed.png")
        
        screenshot.save(filename_original)
        
        if ocr:
            # Save preprocessed version of the image
            gray_image = screenshot.convert("L")
            inverted_image = Image.fromarray(255 - np.array(gray_image))
            thresholded_image = inverted_image.point(lambda p: p > 128 and 255)
            thresholded_image.save(filename_preprocessed)

def extract_text_to_right(screenshot, location, screenshot_logs_dir):
    # Expand the vertical bounds by 2 pixels up and down
    expanded_top = max(0, location.top - 2)
    expanded_bottom = min(screenshot.height, location.top + location.height + 3)

    # Define the expanded region to the right of the detected pattern
    text_region = (
        location.left + location.width,
        expanded_top,
        screenshot.width - (location.left + location.width),
        expanded_bottom - expanded_top
    )

    # Crop the text region from the screenshot
    cropped_text_image = screenshot.crop((
        text_region[0],
        text_region[1],
        text_region[0] + text_region[2],
        text_region[1] + text_region[3]
    ))

    # Convert to grayscale
    gray_image = cropped_text_image.convert("L")

    # Invert colors
    inverted_image = Image.fromarray(255 - np.array(gray_image))

    # Apply binary thresholding
    thresholded_image = inverted_image.point(lambda p: p > 128 and 255)

    # Save the preprocessed image in the screenshot_logs_dir
    preprocessed_image_path = os.path.join(script_dir, screenshot_logs_dir, "preprocessed_image.png")
    thresholded_image.save(preprocessed_image_path)

    # Perform OCR with improved configuration for space detection
    custom_config = (
        "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
        "-c tessedit_char_blacklist='\"!@#$%^&*()[]{}<>;:|`~'"
        "-c tessedit_write_unlv=1"
        "-c textord_min_space=1"
    )
    text = pytesseract.image_to_string(thresholded_image, config=custom_config)

    return text.strip()

def main(screen_x_range, screen_y_range, alert_images, verbose, nodisk, ocr, frequency):
    global detected_counter, screenshot_counter, screenshot_logs_dir  # Declare global variables

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
                    for alert_image in alert_images:
                        location = is_pattern_present(alert_image, screenshot)
                        if location:
                            detected = True
                            screenshot_modified = highlight_pattern(screenshot.copy(), location)
                            save_screenshot_with_timestamp(screenshot_modified, alert_image, screenshot_logs_dir, nodisk)

                            if ocr:
                                extracted_text = extract_text_to_right(screenshot, location, screenshot_logs_dir)
                                log_message(f"Pattern {alert_image} detected! Offending player's name (experimental): {extracted_text}")
                            else:
                                log_message(f"Pattern {alert_image} detected!")

                            if detected_counter > 1:
                                sound_file = sounds[alert_image]
                                pygame.mixer.Sound(sound_file).play()
                                log_message(f"Sound played.")
                                time.sleep(1.5)
                                break
                            else:
                                log_message(f"Below detected_counter threshold, so no sound played.")

                    if detected:
                        detected_counter += 1
                        if verbose:
                            log_message(f"Detected Counter at {detected_counter} since pattern was detected.")
                        if detected_counter > 20:
                            detected_counter = 5
                    else:
                        detected_counter = 0
                        if verbose:
                            log_message(f"Detected Counter at {detected_counter} since pattern was not detected.")

                    save_latest_screenshot(screenshot, screenshot_logs_dir, nodisk, ocr)
                    time.sleep(frequency)

    except KeyboardInterrupt:
        log_message("\nScript stopped.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Search for patterns on the screen and play sounds when detected.")
    parser.add_argument("--screenx", type=str, default="0,1920", help="Screen region for x dimension (start,end)")
    parser.add_argument("--screeny", type=str, default="0,1080", help="Screen region for y dimension (start,end)")
    parser.add_argument("--alertimages", default="terrible.png", nargs="+", help="Filenames of alert images")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode to print additional messages")
    parser.add_argument("--nodisk", action="store_true", help="Disables storing screenshots to the disk")
    parser.add_argument("--ocr", action="store_true", help="Enables experimental feature to read the name in Local chat (using Compact Member List)")
    parser.add_argument("--frequency", type=float, default=0.5, help="Frequency of taking screenshots in seconds")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    verbose = args.verbose  # Store the value of verbose for later use
    nodisk = args.nodisk  # Store the value of nodisk for later use
    main(args.screenx, args.screeny, args.alertimages, args.verbose, args.nodisk, args.ocr, args.frequency)