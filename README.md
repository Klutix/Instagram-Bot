# Kokigram

Instagram like-bot for Windows (not tested on Linux)

## Installation

Download or clone the directory.

## Requirements

Python, sqlite3, selenium

## Usage

```python
import instagram_automation

if __name__ == "__main__":    
    i = instagram_automation()   # starts the bot
    i.cmd_in()                   # start the input loop
    del i                        # delete the object to kill bot
    exit()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GNU](https://choosealicense.com/licenses/gnu/)
