#!/usr/bin/env python
"""Proxies commands to the actual vale found in `vale_bin`."""
import subprocess
import sys
from pathlib import Path

import vale

def main():
    """Download vale if not downloaded and executes it."""
    vale_bin_path = Path(vale.__file__).parent / "vale_bin"

    proc = subprocess.run([f"{vale_bin_path}"] + sys.argv[1:])

    sys.exit(proc.returncode)
