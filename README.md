# Red Alert

This Python3 script should be run on your Windows computer in a separate offscreen terminal while playing the game.  It will alert you if there is a "Bad" or "Terrible" player on your screen both audibly and via text output via the terminal.


## Changelog

### Version 0.2.0
* TBD Added box drawing capability, so x,y coordinate input becomes optional and the user can draw a box of the area that they wish for the script to watch

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


## Screenshot Parameters and Tips

This script works by frequently taking a screenshot of an area of your monitor that you define (via screenx and screeny parameters) and it compares it against one or more image patterns that you define (via alertimages parameter).  This script comes with a few image files to help you get started.  If this script sees a match of what's on your screen against the images you tell it to look for, it will make a sound or flash the screen yellow (depending on preference) and output some text in your PowerShell window.  You can further refine this by alerting on a minimum number of matches by using the `--a_threshold #` and/or `--v_threshold #` arguments.

The screenx parameter is the X-coordinate of your screenshot, where the first number is the starting position and the second number is your ending position.  So, if you define `--screenx 100,500`, it will take screenshots from the 100th pixel from the left, all the way to the 500th pixel from the left, for a total of 400 pixels wide.

The screeny parameter is the Y-coordinate of your screenshot, where the first number is the starting position and the second number is your ending position.  So, if you define `--screeny 200,800`, it will take screenshots from the 200th pixel from the top, all the way to the 800th pixel from the top, for a total of 600 pixels high.

Combining the screenx and screeny parameters gives you a rectangular area of your screen that this tool will take a screenshot of.  The smaller this screenshot, the faster the Python script will run and the less resource-intensive the tool will be when it's running.

You should set your screen parameters (--screenx and --screeny) to your Local window.  You can use the "screenshot_logs" directory and the "latest_screenshot.png" file to determine the current view that the script sees when it's running.  Once you have the tool working for you and you verified the screenshots are taking the section of the screen that you expect it to, you can improve the tool's performance by passing the `--nodisk` option which will stop the script from saving screenshots to your disk.


## Set Up - Run These Once

1. Install the latest version of Python3 from Microsoft Store: https://apps.microsoft.com/search/publisher?name=Python+Software+Foundation&hl=en-us&gl=US
(This script has been tested with Python3.12)
2. Open PowerShell
3. Copy and paste the following, then press Enter: `pip3 install pyautogui`
4. Copy and paste the following, then press Enter: `pip3 install pygame`
5. Copy and paste the following, then press Enter: `pip3 install numpy`
6. Copy and paste the following, then press Enter: `pip3 install Pillow`
7. Copy and paste the following, then press Enter: `pip3 install mss`
8. Copy and paste the following, then press Enter: `pip3 install pyscreeze`
9. Copy and paste the following, then press Enter: `pip3 install opencv-python`


## Normal Usage

1. Open PowerShell
2. Change directory to where this code is on your computer by using the `cd` command, entering in the directory, and then pressing Enter
3. Copy and paste the following, then press Enter: `python3 main.py --screenx 0,1920 --screeny 0,1440 --alertimages terrible.png`
4. When you want to quit, click on your PowerShell session, hold CTRL key, and press the C key


## Known Limitations and other FAQ

* The function `pyautogui.locate` does not see colors, so "Bad" and "Terrible" will both alarm
* The images that are included with this script called "terrible.png" and "neutral.png" may not work if you have changed how these appear in your game client - overwrite or include new images as you deem appropriate
* This script must be run from the same working directory - it must be `python3 main.py --options args` and not `python3 C:\Users\Desktop\etc\main.py --options args`
