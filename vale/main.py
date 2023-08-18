#!/usr/bin/env python
"""Downloads Vale if not downloaded yet and executes it."""

import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from functools import partial
from pathlib import Path
from typing import Optional, Tuple
from urllib.request import urlopen

import vale

if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata


def major_minor_patch(version: str) -> str:
    """E.g.: 2.20.0.1 -> 2.20.0 ."""
    return ".".join(version.split(".")[0:3])


# We download the Vale version corresponding to this Python package's version
# (see pyproject.toml) up to major, minor and patch (3 numbers). This Python
# package uses a 4th number to account for fixes to this package, which will be
# ignored here. That 4th number is needed because PyPi doesn't allow to
# re-release or upload deleted versions, every uploaded version must be unique.
vale_bin_version = major_minor_patch(importlib_metadata.version("vale"))


def get_target() -> Tuple[str, str, str]:
    """Return Vale's target OS, architecture and extension to download."""
    operating_system: Optional[str] = None
    architecture: Optional[str] = None

    if sys.platform.startswith("linux"):
        operating_system = "Linux"
    elif sys.platform.startswith("darwin"):
        operating_system = "macOS"
    elif sys.platform.startswith("win32"):
        operating_system = "Windows"

    if platform.processor() == "arm":
        architecture = "arm"
    else:
        convert_arch = {"32bit": "32-bit", "64bit": "64-bit"}
        architecture = convert_arch.get(platform.architecture()[0], None)

    if not operating_system:
        raise RuntimeError(
            f"Operating system '{sys.platform}' not supported. "
            "Supported operating systems are 'linux', 'darwin' and 'win32'."
        )
    if not architecture:
        raise RuntimeError(
            f"Architecture {os.uname().machine} not supported. "
            "Supported architectures are 'x86_64' and 'arm'"
        )

    if operating_system == "Windows":
        extension = "zip"
    else:
        extension = "tar.gz"

    return operating_system, architecture, extension


def extract_vale(
    archive: str, extension: str, destination: str, bin_name: str = "vale"
) -> str:
    """Extract `vale` binary from the given archive."""
    if extension == "zip":
        archiver = zipfile.ZipFile
    elif extension == "tar.gz":
        archiver = partial(tarfile.open, mode="r:gz")  # type: ignore
    else:
        raise ValueError(
            f"Archive type '{extension}' is not supported. "
            "Only 'zip' and 'tar.gz' supported."
        )

    with archiver(archive) as archive_volume:
        archive_volume.extractall(destination)

    vale_tmp_path = Path(destination) / bin_name

    assert vale_tmp_path.exists()

    return f"{vale_tmp_path}"


def download_vale_if_missing() -> str:
    """Download vale only if missing."""
    vale_bin_path = Path(vale.__file__).parent / "vale_bin"

    # We have a dummy vale placeholder that is overwritten by the downloaded
    # vale version. See `vale/vale_bin` (in this repo, not in its installed
    # form) for more details about this magic number of bytes.
    if vale_bin_path.stat().st_size < 1000:

        print("* vale not found. Downloading it...")

        operating_system, architecture, extension = get_target()

        url_str = (
            "https://github.com/errata-ai/vale/releases/download"
            f"/v{vale_bin_version}/"
            f"vale_{vale_bin_version}_{operating_system}_{architecture}"
            f".{extension}"
        )

        url = urlopen(url_str)

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_dir_path = Path(temp_dir)

            archive_temp_file_path = temp_dir_path / "vale.zip"

            with open(str(archive_temp_file_path), "wb") as archive_temp_file:

                archive_temp_file.write(url.read())

                print(f"* {url_str} downloaded to {archive_temp_file.name}")

                archive_temp_dir_path = temp_dir_path / "vale_unzipped"

                archive_temp_dir_path.mkdir()

                archive_bin_name = (
                    "vale.exe" if operating_system == "Windows" else "vale"
                )

                vale_tmp_path = extract_vale(
                    archive=str(archive_temp_file_path),
                    extension=extension,
                    destination=str(archive_temp_dir_path),
                    bin_name=archive_bin_name,
                )

                print(f"* Copying {vale_tmp_path} to {vale_bin_path}")
                shutil.copy(f"{vale_tmp_path}", f"{vale_bin_path}")

        print("* vale extracted and copied to module path.")

    return f"{vale_bin_path}"


def main():
    """Download vale if not downloaded and executes it."""
    vale_bin_path = download_vale_if_missing()

    proc = subprocess.run([f"{vale_bin_path}"] + sys.argv[1:])
    sys.exit(proc.returncode)
