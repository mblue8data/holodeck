# rainbow_ascii.py

import random

text = r"""
   __          __          __          __
  / /_  ____  / /___  ____/ /__  _____/ /__
 / __ \/ __ \/ / __ \/ __  / _ \/ ___/ //_/
/ / / / /_/ / / /_/ / /_/ /  __/ /__/ ,<
/_/ /_/\____/_/\____/\__,_/\___/\___/_/|_|
"""

# ANSI color codes
colors = [
    '\033[91m',  # Red
    '\033[93m',  # Yellow
    '\033[92m',  # Green
    '\033[96m',  # Cyan
    '\033[94m',  # Blue
    '\033[95m',  # Magenta
]
reset = '\033[0m'

for line in text.splitlines():
    colored_line = ''.join(random.choice(colors) + c for c in line)
    print(colored_line + reset)
