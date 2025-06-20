# Red Alert

This is a Python3 tool that runs alongside your game to help identify undesirable players. It scans part of your screen in real-time and notifies you if it detects a "Bad" or "Terrible" player, using both visual and sound alerts.

Use this tool in a separate window while your game is running. It works best when customized to your screen and alert preferences.


## Set Up - Run These Once

1. Install the latest version of Python3 from Microsoft Store: https://apps.microsoft.com/search/publisher?name=Python+Software+Foundation&hl=en-us&gl=US
(This script has been tested with Python3.12)
2. Open PowerShell (search for "PowerShell" in the Start menu)
3. Install the required Python packages by running these commands one by one:
 * Copy and paste the following, then press Enter: `pip3 install pyautogui`
 * Copy and paste the following, then press Enter: `pip3 install pygame`
 * Copy and paste the following, then press Enter: `pip3 install numpy`
 * Copy and paste the following, then press Enter: `pip3 install Pillow`
 * Copy and paste the following, then press Enter: `pip3 install mss`
 * Copy and paste the following, then press Enter: `pip3 install pyscreeze`
 * Copy and paste the following, then press Enter: `pip3 install opencv-python`


## Example Usage with Common Options

1. Open PowerShell (search for "PowerShell" in the Start menu)
2. Change directory to where this code is on your computer by using the `cd` command, entering in the directory, and then pressing Enter
3. Copy and paste the following, then press Enter: `python3 main.py --alertimages terrible.png neutral.png --a_threshold 2 --vt_red 3 --vt_yellow 2 --vt_gray 1`
4. When you want to quit, click on your PowerShell session, hold CTRL key, and press the C key


## Screenshot Region Selection and Performance Tips

When the script starts, it needs to know which part of your screen to monitor. You can define this area in one of two ways:

### Option 1 - Draw a Box
If you don’t provide coordinates, a transparent screen will appear. Use your mouse to click and drag a rectangle over the part of the screen you want the script to monitor (such as your game's local window or overview). The area inside this rectangle will be used for image matching.

Press Esc if you want to cancel and exit the selection.

### Option 2 - Manually Define Coordinates
Use the --screenx and --screeny options if you want to set a custom screen area without drawing it.

--screenx start,end → Horizontal range in pixels (left to right)
Example: --screenx 100,500 captures from pixel 100 to 500 (400 pixels wide)

--screeny start,end → Vertical range in pixels (top to bottom)
Example: --screeny 200,800 captures from pixel 200 to 800 (600 pixels high)

Smaller screen regions are faster and use less resources.


## Tips for Best Results

You can preview what the script is seeing by checking the file, if you add the `--screenshots` parameter:
screenshot_logs/latest_screenshot_original.png

Once you're confident the screenshot area is correct, you can disable file-saving (to improve performance) by simply not including the `--screenshots` parameter.

The script prioritizes visual alerts in this order:
Red > Yellow > Gray


## Changelog

### Version 0.2.0
* Added box drawing capability, so x,y coordinate input becomes optional
* The --nodisk parameter has been removed, and its behavior is now the default
* The --screenshots parameter has been added, which, if supplied, will store screenshot files to the disk
* Removed --v_threshold, as this will be broken up into colors
* Added --vt_red, which is the threshold of number of matches for a Red-colored visual alert (highest priority)
* Added --vt_yellow, which is the threshold of number of matches for a Yellow-colored visual alert
* Added --vt_gray, which is the threshold of number of matches for a Gray-colored visual alert (lowest priority)
* Increased Visual Alert blink rate

### Version 0.1.1
* Minor bugfix to threshold values

### Version 0.1.0
* Visual Warning introduced and can be set to activate upon a number of matches via argument --v_threshold
* Audio Warning now optional and can be set to activate upon a number of matches via argument --a_threshold
* Removed --match_threshold as that is now replaced by --a_threshold and --v_threshold
* Removed OCR experimental feature as its performance was too poor
* Removed --verbose and added --loglevel

### Version 0.0.4
* Match Threshold introduced

### Version 0.0.3
* OCR experimental feature added
* Added default icons for Overview

### Version 0.0.2
* Multi-monitor support added

### Version 0.0.1
* Initial Version


## Known Limitations and other FAQ

* The function `pyautogui.locate` does not see colors, so "Bad" and "Terrible" will both alarm
* The images that are included with this script called "terrible.png" and "neutral.png" may not work if you have changed how these appear in your game client - overwrite or include new images as you deem appropriate
* This script must be run from the same working directory - it must be `python3 main.py --options args` and not `python3 C:\Users\Desktop\etc\main.py --options args`
