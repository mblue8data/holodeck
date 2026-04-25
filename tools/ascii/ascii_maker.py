import argparse
import subprocess
from pyfiglet import Figlet
import shutil
import sys


def generate_ascii(text, font="slant", output_file=None, use_lolcat=False):
    columns, _ = shutil.get_terminal_size()
    figlet = Figlet(font=font, width=columns)
    ascii_art = figlet.renderText(text)

    if use_lolcat and shutil.which("lolcat"):
        # Use subprocess to pipe the text through lolcat
        process = subprocess.Popen(["lolcat"], stdin=subprocess.PIPE)
        process.communicate(ascii_art.encode())
    else:
        print(ascii_art)

    if output_file:
        with open(output_file, "w") as f:
            f.write(ascii_art)
        print(f"✅ Saved to {output_file}")

def list_fonts():
    figlet = Figlet()
    fonts = figlet.getFonts()
    print("🧵 Available fonts:")
    for font in fonts:
        print(f"  - {font}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turn text into glorious ASCII art.")
    parser.add_argument("text", nargs="?", help="The text to convert")
    parser.add_argument("-f", "--font", default="slant", help="Font to use (default: slant)")
    parser.add_argument("-o", "--output", help="Optional file to save output")
    parser.add_argument("--list-fonts", action="store_true", help="List all available fonts")
    parser.add_argument("--lolcat", action="store_true", help="Use lolcat to colorize output")

    args = parser.parse_args()

    if args.list_fonts:
        list_fonts()
    elif args.text:
        generate_ascii(args.text, font=args.font, output_file=args.output, use_lolcat=args.lolcat)
    else:
        print("❗ Please provide text or use --list-fonts")

