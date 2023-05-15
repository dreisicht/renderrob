import sys
from datetime import datetime
from sty import RgbBg, Style, bg, fg, rs


def print_info(message: str) -> None:
  """Prints info to the console with a timestamp."""
  time_current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  print(time_current, message)


def print_info_input(message: str) -> None:
  """Prints info to the console with a timestamp."""
  bg.dark_blue = Style(
      RgbBg(69, 129, 142))
  time_current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  input(bg.dark_blue + fg.white + time_current +
        "[INFO] " + message + " press Enter to continue." + rs.all)


def print_error(message: str) -> None:
  """Prints error to the console with a timestamp."""
  time_current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  bg.red = Style(RgbBg(152, 0, 48))
  input(bg.red + fg.white + time_current +
        " [ERROR] " + message + " Press Enter to exit." + rs.all)
  sys.exit()


def print_warning(message: str) -> None:
  """Prints warning to the console with a timestamp."""
  time_current = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  bg.yellow = Style(RgbBg(255, 217, 102))
  input(bg.yellow + fg.black + time_current +
        "[WARNING] " + message + " Press Enter to continue." + rs.all)
