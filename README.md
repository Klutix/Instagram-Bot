# Kokigram

Instagram like-bot for Windows (not tested on Linux)

![Instagram Like-bot](https://github.com/Klutix/Images/blob/master/instagram%20like%20bot.png)


## Installation

Download or clone the directory.


## Requirements

Python, sqlite3, selenium, chromedriver.exe

Different versions chromedriver can be found @ http://chromedriver.chromium.org/downloads

## Configuration File

A configuration file is included in this repo, although the program does generate a sample config when one first run if none exist.

It is recommend to set your <google_profile_path>. Although if that gives you trouble you can set <use_login> to 1 and provide login credientials.

```bash
[LOGIN]
use_login = 0
username = USERNAME
password = PASSWORD
google_profile_path = C:\Users\USERNAME\AppData\Local\Google\Chrome\User Data

[BOT_CONFIG]
like_limit_per_catgeory = 30
like_delay_range = 36 70
scroll_count = 5
categories = #fractalart #fractals #prettyArt
```
**like_limit_per_catgeory** -Limit of likes per category

**like_delay_range** - Determines the sleep time range between likes. (DO NOT SET TOO LOW IF YOU VALUE YOUR ACCOUNT) Recommended speed is 36 70.

**scroll_count** - Number scrolls you used when collecting urls to like. (Increase this if you notice your *skips* are high and its effecting *Urls Available* or *Urls in Queue too Low* and lower then your *limit* set in config.

**categories** - All catagories you wish to navigate through. **must have be #category** seperated by **space**.

## Usage

You can use the executable in the *Dist* folder or you import into a script and use like:

**!!make sure all other instances of chrome are closed before running bot!! once the bot has opened its own chrome instance feel free to do as you please with your own instances. If the bots instance is closed you must restart the bot!!**

```python
import instagram_automation

if __name__ == "__main__":    
    i = instagram_automation()   # starts the bot
    i.cmd_in()                   # start the input loop
    del i                        # delete the object to kill bot
    exit()
```
remember to include the chromedriver.exe in the same folder as the script or executable.
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GNU](https://choosealicense.com/licenses/gnu/)
