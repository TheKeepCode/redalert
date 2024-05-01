# Red Alert

This Python3 script should be run on your Windows computer in a separate offscreen terminal while playing the game.  It will alert you if there is a "Bad" or "Terrible" player on your screen both audibly and via text output via the terminal.

## Changelog

### Version 0.0.1
* Allows for alternative monitor to be specified

## Screenshot Parameters and Tips

This script works by frequently taking a screenshot of an area of your monitor that you define (via screenx and screeny parameters) and it compares it against one or more image patterns that you define (via alertimages parameter).  This script comes with two files, one called "terrible.png" and another called "neutral.png" to help you get started.  If this script sees a match of what's on your screen against the images you tell it to look for, it will make a sound and output some text in your PowerShell window.

The screenx parameter is the X-coordinate of your screenshot, where the first number is the starting position and the second number is your ending position.  So, if you define `--screenx 100,500`, it will take screenshots from the 100th pixel from the left, all the way to the 500th pixed from the left, for a total of 400 pixels wide.

The screeny parameter is the Y-coordinate of your screenshot, where the first number is the starting position and the second number is your ending position.  So, if you define `--screeny 200,800`, it will take screenshots from the 200th pixel from the top, all the way to the 800th pixed from the top, for a total of 600 pixels high.

Combining the screenx and screeny parameters gives you a square - a rectangular area of your screen that this tool will take a screenshot of.  The smaller this screenshot, the faster the Python script will run and the less resource-intensive the tool will be when it's running.

You should set your screen parameters (--screenx and --screeny) to your Local window.  You can use the "screenshot_logs" directory and the "latest_screenshot.png" file to determine the current view that the script sees when it's running.  Once you have the tool working for you and you verified the screenshots are taking the section of the screen that you expect it to, you can improve the tool's performance by passing the `--nodisk` option which will stop the script from saving screenshots to your disk.


## Set Up - Run These Once

1. Install the latest version of Python3 from Microsoft Store: https://apps.microsoft.com/search/publisher?name=Python+Software+Foundation&hl=en-us&gl=US
 * This script has been tested with Python3.12
2. Open PowerShell
3. Copy and paste the following, then press Enter: `pip3 install pyautogui`
4. Copy and paste the following, then press Enter: `pip3 install pygame`
5. Copy and paste the following, then press Enter: `pip3 install numpy`
6. Copy and paste the following, then press Enter: `pip3 install Pillow`
7. Copy and paste the following, then press Enter: `pip3 install mss`


## Normal Usage

1. Open PowerShell
2. Change directory to where this code is on your computer by using the `cd` command, entering in the directory, and then pressing Enter
3. Copy and paste the following, then press Enter: `python3 main.py --screenx 0,1920 --screeny 0,1440 --alertimages terrible.png`
4. When you want to quit, click on your PowerShell session, hold CTRL key, and press the C key


## Known Limitations and other FAQ

* This script can only read from the primary monitor
* The function `pyautogui.locate` does not see colors, so "Bad" and "Terrible" will both alarm
* The images that are included with this script called "terrible.png" and "neutral.png" may not work if you have changed how these appear in your game client - overwrite or include new images as you deem appropriate
* This script must be run from the same working directory - it must be `python3 main.py --options args` and not `python3 C:\Users\Desktop\etc\main.py --options args`
