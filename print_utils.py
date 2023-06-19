"""Utility functions for printing to the console."""
import sys
import time

RESET_ALL = '\u001b[0m'
BACK_CYAN = '\u001b[46m'
BACK_RED = '\u001b[41m'
BACK_YELLOW = '\u001b[43m'
FORE_BLACK = '\u001b[30m'
FORE_WHITE = '\u001b[37m'


def hex_to_rgb(hex_col):
  """Convert hex color to RGB color."""
  return tuple(int(hex_col[i:i + 2], 16) for i in (0, 2, 4))


def to_bool(bool_val):
  """Convert a string or int to a bool."""
  if isinstance(bool_val, str):
    if bool_val.upper() == "FALSE":
      return False
    if bool_val.upper() == "TRUE":
      return True
    raise ValueError("Could not convert value to bool.")
  if isinstance(bool_val, int):
    if bool_val == 0:
      return False
    if bool_val == 1:
      return True
  raise ValueError("The value is not a string or int.")


def print_error(ipt_str):
  """Print an error message to the console and exit the program."""
  ipt_str = str(ipt_str)
  print(BACK_RED, FORE_WHITE, end="")
  print("[ERROR] " + ipt_str + " Exiting in 3 seconds.")
  print(RESET_ALL, end="")
  write_cache("[ERROR]" + ipt_str)
  time.sleep(3)
  sys.exit()


def print_warning(ipt_str):
  """Print a warning message to the console."""
  ipt_str = str(ipt_str)
  print(BACK_YELLOW, FORE_BLACK, end="")
  print("[WARNING] " + ipt_str)
  print(RESET_ALL, end="")
  write_cache("[WARNING]" + ipt_str)
  time.sleep(1)


def print_info_input(ipt_str):
  """Print an info message to the console and wait for user input."""
  ipt_str = str(ipt_str)
  print(BACK_CYAN, FORE_BLACK, end="")
  input("[INFO] " + ipt_str)
  print(RESET_ALL, end="")


def print_info(ipt_str):
  """Print an info message to the console."""
  ipt_str = str(ipt_str)
  print(BACK_CYAN, FORE_BLACK + "[INFO] " + ipt_str + RESET_ALL)


def write_cache(ipt_str):
  """Write an error message to the error cache."""
  cachefilepath = "util/ERRORCACHE"
  try:
    f = open(cachefilepath, "a", encoding="utf-8")
  except PermissionError:
    time.sleep(0.1)
    f = open(cachefilepath, "a", encoding="utf-8")
  finally:
    time.sleep(0.1)
  f.write(ipt_str + "\n")
  f.close()
