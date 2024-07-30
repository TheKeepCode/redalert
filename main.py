import cv2
import numpy as np
from PIL import Image
import pyautogui
import argparse
import datetime
import os
import time
import mss
import pygame

# Get the directory path of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize pygame for playing sounds
pygame.init()

# Global variable to keep track of modified screenshots
modified_screenshots = []
detected_counter = 0

def compare_histograms(pattern_image, screenshot, threshold=0.8):
    # Convert images to numpy arrays
    screenshot_np = np.array(screenshot)
    pattern_np = np.array(pattern_image)

    # Convert to HSV color space
    screenshot_hsv = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2HSV)
    pattern_hsv = cv2.cvtColor(pattern_np, cv2.COLOR_BGR2HSV)

    # Compute histograms and compare using correlation
    hist_screenshot = cv2.calcHist([screenshot_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
    hist_pattern = cv2.calcHist([pattern_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])

    cv2.normalize(hist_screenshot, hist_screenshot, 0, 1, cv2.NORM_MINMAX)
    cv2.normalize(hist_pattern, hist_pattern, 0, 1, cv2.NORM_MINMAX)

    similarity = cv2.compareHist(hist_screenshot, hist_pattern, cv2.HISTCMP_CORREL)

    return similarity >= threshold, None

def load_sounds(alert_images):
    sounds = {}
    for alert_image in alert_images:
        sounds[alert_image] = os.path.join(script_dir, "beep.wav")  # Hardcoded sound file name
    return sounds

def save_screenshot_with_timestamp(screenshot, alert_image, screenshot_logs_dir, nodisk):
    if not nodisk:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-1]
        filename = os.path.join(script_dir, screenshot_logs_dir, f"screenshot_{timestamp}_{alert_image}")
        screenshot.save(filename)
        modified_screenshots.append(filename)
        if len(modified_screenshots) > 10:
            os.remove(modified_screenshots.pop(0))

def highlight_pattern(image, location, pattern_size):
    draw = ImageDraw.Draw(image)
    left, top = location
    right, bottom = left + pattern_size[0], top + pattern_size[1]
    draw.rectangle([left, top, right, bottom], outline="yellow", width=2)
    return image

def save_latest_screenshot(screenshot, screenshot_logs_dir, nodisk):
    if not nodisk:
        filename = os.path.join(script_dir, screenshot_logs_dir, "latest_screenshot.png")
        screenshot.save(filename)

def main(screen_x_range, screen_y_range, alert_images, verbose, nodisk, frequency):
    global detected_counter, modified_screenshots

    start_x, end_x = map(int, screen_x_range.split(','))
    start_y, end_y = map(int, screen_y_range.split(','))
    screen_width, screen_height = pyautogui.size()

    sounds = load_sounds(alert_images)

    screenshot_logs_dir = os.path.join(script_dir, "screenshot_logs")
    if not os.path.exists(screenshot_logs_dir):
        os.makedirs(screenshot_logs_dir)
    else:
        for filename in os.listdir(screenshot_logs_dir):
            file_path = os.path.join(screenshot_logs_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    try:
        with mss.mss() as sct:
            while True:
                detected = False
                screenshot = sct.grab({"top": start_y, "left": start_x, "width": end_x - start_x, "height": end_y - start_y})
                screenshot = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                for alert_image in alert_images:
                    pattern_image = Image.open(alert_image)
                    pattern_size = pattern_image.size

                    # Debugging: Ensure template size is correctly smaller than the screenshot
                    print(f"Checking pattern: {alert_image}")
                    detected, location = compare_histograms(pattern_image, screenshot)
                    if detected:
                        screenshot_modified = highlight_pattern(screenshot.copy(), location, pattern_size)
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
    main(args.screenx, args.screeny, args.alertimages, args.verbose, args.nodisk, args.frequency)
