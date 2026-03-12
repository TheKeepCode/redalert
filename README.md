# Red Alert

This is a Python 3.12 tool that runs alongside your game to help identify undesirable players. It scans part of your screen in real-time and notifies you if it detects a "Bad" or "Terrible" player, using both visual and sound alerts.

Use this tool in a separate window while your game is running. It works best when customized to your screen and alert preferences.


## Set Up - Run These Once

1. Install the latest version of Python 3.12 from Microsoft Store: https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-US&gl=US
(This script has been tested with Python 3.12.10)
2. Open PowerShell (search for "PowerShell" in the Start menu)
3. Install the required Python packages by running these commands one by one:
 * Copy and paste the following, then press Enter: `pip3 install pyautogui`
 * Copy and paste the following, then press Enter: `pip3 install pygame`
 * Copy and paste the following, then press Enter: `pip3 install numpy`
 * Copy and paste the following, then press Enter: `pip3 install Pillow`
 * Copy and paste the following, then press Enter: `pip3 install mss`
 * Copy and paste the following, then press Enter: `pip3 install pyscreeze`
 * Copy and paste the following, then press Enter: `pip3 install opencv-python`
4. Restart the Computer
5. Open PowerShell (search for "PowerShell" in the Start menu)
6. Ensure Python is installed by copy and pasting the following, then pressing Enter: `python --version`
 * This should report Python 3.12


## How to Use

1. Open PowerShell (search for "PowerShell" in the Start menu)
2. Change directory to where this code is on your computer by using the `cd` command, entering in the directory, and then pressing Enter
3. Copy and paste the following, then press Enter: `python main.py --help`
4. This will explain all of the inputs that the module supports and what the inputs do


## Example Usage with Common Options

1. Open PowerShell (search for "PowerShell" in the Start menu)
2. Change directory to where this code is on your computer by using the `cd` command, entering in the directory, and then pressing Enter
3. Copy and paste the following, then press Enter: `python main.py --alertimages terrible.png neutral.png --a_threshold 2 --vt_red 3 --vt_yellow 2 --vt_gray 1`
4. When you want to quit, click on your PowerShell session, hold CTRL key, and press the C key


## Screenshot Region Selection and Performance Tips

When the script starts, it needs to know which part of your screen to monitor. You can define this area in one of two ways:

### Option 1 - Draw a Box
If you don’t provide coordinates, a transparent screen will appear. Use your mouse to click and drag a rectangle over the part of the screen you want the script to monitor (such as your game's local window or overview). The area inside this rectangle will be used for image matching.

Press Esc if you want to cancel and exit the selection.

### Option 2 - Manually Define Coordinates
Use the `--screenx` and `--screeny` options if you want to set a custom screen area without drawing it.

`--screenx start,end` → Horizontal range in pixels (left to right)
Example: `--screenx 100,500` captures from pixel 100 to 500 (400 pixels wide)

`--screeny start,end` → Vertical range in pixels (top to bottom)
Example: `--screeny 200,800` captures from pixel 200 to 800 (600 pixels high)

Smaller screen regions are faster and use less resources.


## Tips for Best Results

You can preview what the script is seeing by checking the file, if you add the `--screenshots` parameter:
screenshot_logs/latest_screenshot_original.png

Once you're confident the screenshot area is correct, you can disable file-saving (to improve performance) by simply not including the `--screenshots` parameter.

The script prioritizes visual alerts in this order:
Red > Yellow > Gray


## Changelog

### Version 0.3.0
* Improved detection logic flow and made it into a state machine, now a single "alerting event" is defined as any time the tool is actively detecting an alert and the "alerting event" is considered over once the threats have been cleared (a value BELOW ALL of the threshold values)
* Added --k_action, which is the keypress action that will be performed when the threshold for this check is met, valid values for this are single keystrokes like `0` or `a` but can also include function keys like `home` or `f12`
* Added --k_threshold, which is the threshold of number of matches for a keypress action
* Added --k_max, which is the maximum number of times a keypress will be performed during the alerting event
* Added --a_max, which is the maximum number of times an audible alert will trigger during the alerting event

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
* This script must be run from the same working directory - it must be `python main.py --options args` and not `python C:\Users\Desktop\etc\main.py --options args`
