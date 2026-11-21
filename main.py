#!/usr/bin/env python3
"""make.fun entry for news-image-20261121 (harness program/v1, Python 3.13, stdlib only).

The image is entry.png beside this file: a one-page summary of the world's news of
Saturday 21 November 2026, built offline with render.py. This program copies that
exact PNG to the grader's output directory, so the judge sees precisely those bytes.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    dst = os.path.join(OUT_DIR, "entry.png")
    shutil.copyfile(SRC, dst)
    # The judge reads exactly these bytes; fail loudly if the copy is short.
    if os.path.getsize(dst) != os.path.getsize(SRC):
        raise SystemExit("entry.png was not copied whole")


if __name__ == "__main__":
    main()
