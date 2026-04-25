#!/bin/bash

# Look at all of the fonts for pyfiglet

# Path to your font list
FONT_FILE="fonts.txt"

# Optional: Clear screen first
clear

# Loop through each font
while IFS= read -r font; do
  # Skip empty lines or comments
  [[ -z "$font" || "$font" == \#* ]] && continue

  echo "Font: $font"
  python3 ascii_maker.py --font "$font" holodeck
  echo -e "\n-----------------------------\n"
  sleep 0.2  # Optional: slow it down so you can read
done < "$FONT_FILE"

