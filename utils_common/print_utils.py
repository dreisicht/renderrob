"""Utility functions for printing to the console."""
import os
import sys

BASH_COLORS = {
    "RESET_ALL": '\u001b[0m',
    "BACK_CYAN": '\u001b[46m',
    "BACK_RED": '\u001b[41m',
    "BACK_YELLOW": '\u001b[43m',
    "FORE_BLACK": '\u001b[30m',
    "FORE_WHITE": '\u001b[37m',
}
CACHEFILEPATH = "ERRORCACHE"


def print_error(ipt_str):
  """Print an error message to the console and exit the program."""
  ipt_str = str(ipt_str)
  print(BASH_COLORS["BACK_RED"], BASH_COLORS["FORE_WHITE"], end="", flush=True)
  print("[ERROR] " + ipt_str, flush=True)
  print(BASH_COLORS["RESET_ALL"], end="", flush=True)
  write_cache("[ERROR]" + ipt_str)
  print_info("Blender quit")
  sys.exit(62097)


def print_error_no_exit(ipt_str):
  """Print an error message to the console and exit the program."""
  ipt_str = str(ipt_str)
  print(BASH_COLORS["BACK_RED"], BASH_COLORS["FORE_WHITE"], end="", flush=True)
  print("[ERROR] " + ipt_str, flush=True)
  print(BASH_COLORS["RESET_ALL"], end="", flush=True)
  write_cache("[ERROR]" + ipt_str)


def print_warning(ipt_str):
  """Print a warning message to the console."""
  ipt_str = str(ipt_str)
  print(BASH_COLORS["BACK_YELLOW"], BASH_COLORS["FORE_BLACK"], end="", flush=True)
  print("[WARNING] " + ipt_str, flush=True)
  print(BASH_COLORS["RESET_ALL"], end="", flush=True)
  write_cache("[WARNING]" + ipt_str)


def print_info_input(ipt_str):
  """Print an info message to the console and wait for user input."""
  ipt_str = str(ipt_str)
  print(BASH_COLORS["BACK_CYAN"], BASH_COLORS["FORE_BLACK"], end="", flush=True)
  input("[INFO] " + ipt_str)
  print(BASH_COLORS["RESET_ALL"], end="", flush=True)


def print_info(ipt_str):
  """Print an info message to the console."""
  ipt_str = str(ipt_str)
  print(BASH_COLORS["BACK_CYAN"], BASH_COLORS["FORE_BLACK"] +
        "[INFO] " + ipt_str + BASH_COLORS["RESET_ALL"], flush=True)


def write_cache(ipt_str):
  """Write an error message to the error cache."""
  if not os.path.exists(CACHEFILEPATH):
    with open(CACHEFILEPATH, "w", encoding="utf-8") as error_cache_file:
      error_cache_file.write("")
  try:
    with open(CACHEFILEPATH, "a", encoding="utf-8") as error_cache_file:
      error_cache_file.write(ipt_str + "\n")
      error_cache_file.close()
  except PermissionError:
    with open(CACHEFILEPATH, "a", encoding="utf-8") as error_cache_file:
      error_cache_file.write(ipt_str + "\n")
      error_cache_file.close()
