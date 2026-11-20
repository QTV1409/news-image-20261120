#!/usr/bin/env python3
"""Entry point: write the front-page image to the output directory.

The image is pre-drawn by render.py and shipped as entry.png; this
program only copies it to $MAKEFUN_OUTPUT_DIR (default /output) after
checking it is a valid PNG under the 1 MiB size guard. Stdlib only.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    with open(SRC, "rb") as f:
        head = f.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        print("entry.png is not a PNG", file=sys.stderr)
        return 1
    size = os.path.getsize(SRC)
    if size > MAX_BYTES:
        print(f"entry.png is {size} bytes, over the 1 MiB guard",
              file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, "entry.png"))
    print(f"wrote {os.path.join(out_dir, 'entry.png')} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
