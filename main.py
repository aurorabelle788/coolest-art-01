# coolest-art-01 entry (Python 3.13, standard library only).
#
# The art is the entry.png beside this file: a lone diver in a glowing
# orange suit before a colossal bioluminescent jellyfish above an
# underwater city, teal and orange. The program copies it to the output
# directory. The file holds JPEG bytes (first bytes FF D8 FF) under the
# name entry.png, which the rules allow: a file is told apart by its
# first bytes, and the name stays entry.png either way.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
# /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import hashlib
import os
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Width and height from a JPEG's first frame header (stdlib only)."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG: missing SOI marker")
    i = 2
    while i + 1 < len(data):
        if data[i] != 0xFF:
            raise ValueError("corrupt JPEG marker stream")
        marker = data[i + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2 : i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2):  # SOF0/1/2: precision, height, width
            height, width = struct.unpack(">HH", data[i + 5 : i + 9])
            return width, height
        i += 2 + length
    raise ValueError("no JPEG frame header found")


def main() -> None:
    src = HERE / "entry.png"
    data = src.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"entry.png is {len(data)} bytes, over the {MAX_BYTES} cap")
    width, height = jpeg_dimensions(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit(f"entry.png is {width}x{height}, over the {MAX_SIDE} cap")
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "entry.png"
    shutil.copyfile(src, dest)
    if hashlib.sha256(dest.read_bytes()).hexdigest() != hashlib.sha256(data).hexdigest():
        raise SystemExit("copied bytes differ from the source image")


if __name__ == "__main__":
    main()
