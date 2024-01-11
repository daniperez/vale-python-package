#!/usr/bin/env python
"""Supporting functions needed to download Vale."""
import shutil
import sys
import tarfile
import tempfile
import zipfile
from functools import partial
from pathlib import Path
from typing import Tuple, List
from urllib.request import urlopen
import vale
import subprocess

if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

# We download the Vale version corresponding to this Python package's version
# (see pyproject.toml) up to major, minor and patch (3 numbers). This Python
#    package uses a 4th number to account for fixes to this package, which will be
#    ignored here. That 4th number is needed because PyPi doesn't allow to
#    re-release or upload deleted versions, every uploaded version must be unique.
vale_python_version = importlib_metadata.version("vale")
vale_bin_version =".".join(vale_python_version.split(".")[0:3])

def get_vale_artifacts() -> List[Tuple[str, str, str]]:
    """Return a list of existing Vale distributions files (os, arch, extension)."""

    operating_systems = ["Linux", "macOS", "Windows"]

    architectures = ["386", "64-bit", "arm64"]

    blacklisted_combinations = [
        ["macOS", "386"],
    ]

    output = [] 

    for os in operating_systems:
        for arch in architectures:
            if [os, arch] not in blacklisted_combinations:
                if os == "Windows":
                    extension = "zip"
                else:
                    extension = "tar.gz"
                output.append((os, arch, extension))

    return output


def major_minor_patch(version: str) -> str:
    """E.g.: 2.20.0.1 -> 2.20.0 ."""
    return ".".join(version.split(".")[0:3])


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


def download_vale(vale_artifact: str) -> str:
    """Download vale."""
    vale_bin_path = Path(vale.__file__).parent / "vale_bin"

    print(f"* Downloading {vale_artifact}...")

    url_str = (
        "https://github.com/errata-ai/vale/releases/download"
        f"/v{vale_bin_version}/"
        f"{vale_artifact}"
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
                "vale.exe" if "Windows" in vale_artifact else "vale"
            )
            archive_extension = (
                "zip" if "Windows" in vale_artifact else "tar.gz"
            )

            vale_tmp_path = extract_vale(
                archive=str(archive_temp_file_path),
                extension=archive_extension,
                destination=str(archive_temp_dir_path),
                bin_name=archive_bin_name,
            )

            print(f"* Copying {vale_tmp_path} to {vale_bin_path}")
            shutil.copy(f"{vale_tmp_path}", f"{vale_bin_path}")

    print("* vale extracted and copied to module path.")

    return f"{vale_bin_path}"

def build_wheel() -> None:
    """Builds a wheel of the package."""
    # Hopefully there's a better way to achieve this?
    from build.__main__ import main
    main([])

def get_platform_tag(os: str, arch: str) -> str:

    os_tag = {
        "Linux": "linux",
        "macOS": "macosx",
        "Windows": "win",
    }
    arch_tag = {
        "386": "i386",
        "64-bit": "x86_64",
        "arm64": "amd64",
    }

    platform_tag = f"{os_tag[os]}-{arch_tag[arch]}".replace(".","_").replace("-","_")

    return platform_tag

def rename_wheel(wheel_file: Path, platform_tag: str) -> None:
    """Renames the wheel to reflect the desired platform tag."""
    subprocess.run(["wheel", "tags", f"--platform-tag={platform_tag}", str(wheel_file)], check=True) 

def build_wheels():
    """Download vale if not downloaded and executes it."""

    for os, arch, extension in get_vale_artifacts():
    
        vale_artifact_name = f"vale_{vale_bin_version}_{os}_{arch}.{extension}"

        download_vale(vale_artifact_name)

        build_wheel()

        platform_tag = get_platform_tag(os, arch)

        wheel_file = Path() / "dist" / f"vale-{vale_python_version}-py3-none-any.whl"

        rename_wheel(wheel_file, platform_tag)
