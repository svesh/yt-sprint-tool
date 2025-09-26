#!/usr/bin/env python3
"""
Version information for YT Sprint Tool
Contains functions for CLI version and Windows .exe version info generation

Copyright (C) 2025 Sergei Sveshnikov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

# Main project version
VERSION = "1.0.0"

# Author and license information
AUTHOR = "Sergei Sveshnikov"
AUTHOR_EMAIL = "svesh87@gmail.com"
LICENSE = "GPL-3.0"
COPYRIGHT_YEAR = 2025

# Project URLs
PROJECT_URL = "https://github.com/svesh/yt-sprint-tool/"
GITHUB_URL = "https://github.com/svesh/yt-sprint-tool/"

# Product descriptions
CLI_DESCRIPTION = "Unified CLI for sprint creation and synchronization"
SYNC_DESCRIPTION = "Synchronize project default sprint with board sprint"
CREATE_DESCRIPTION = "Create ISO-week sprint on a YouTrack board"

# General information
PROJECT_NAME = "YT Sprint Tool"


def get_version_for_argparse(tool_name: str) -> str:
    """Return version information for argparse version flag."""

    description = CLI_DESCRIPTION if tool_name == "ytsprint" else f"{PROJECT_NAME} - Tool"

    return (
        f"{PROJECT_NAME} {VERSION} | {description} | Author: {AUTHOR} | "
        f"License: {LICENSE} | {PROJECT_URL} | © {COPYRIGHT_YEAR}"
    )


def generate_windows_version_info(
    filename: str,
    version: str = VERSION,
    description: str = "",
    product_name: str = "",
) -> str:
    """Generate .rc file contents with version information for PyInstaller."""

    # Parse version into Windows format (4 numbers)
    version_parts = version.split(".")
    while len(version_parts) < 4:
        version_parts.append("0")

    version_tuple = ",".join(version_parts[:4])
    version_string = ".".join(version_parts[:3])

    year = COPYRIGHT_YEAR
    email = AUTHOR_EMAIL
    url = PROJECT_URL

    rc_content = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'{AUTHOR}'),
            StringStruct(u'FileDescription', u'{description}'),
            StringStruct(u'FileVersion', u'{version_string}'),
            StringStruct(u'InternalName', u'{filename}'),
            StringStruct(u'LegalCopyright', u'Copyright (c) {year} {AUTHOR}. Email: {email}'),
            StringStruct(u'OriginalFilename', u'{filename}'),
            StringStruct(u'ProductName', u'{product_name}'),
            StringStruct(u'ProductVersion', u'{version_string}'),
            StringStruct(u'Comments', u'YouTrack Sprint automation tool. {url}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]

)'''

    return rc_content


def generate_windows_version_files() -> None:
    """Generate version info file for the unified Windows executable."""

    unified_version = generate_windows_version_info(
        filename="ytsprint.exe",
        description=CLI_DESCRIPTION,
        product_name="YT Sprint Tool",
    )

    with open("ytsprint_version.py", "w", encoding="utf-8") as file_handle:
        file_handle.write(unified_version)

    print("Version info files generated:")
    print("  - ytsprint_version.py")


if __name__ == "__main__":
    generate_windows_version_files()
