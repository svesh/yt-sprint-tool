#!/usr/bin/env python3
"""
Tests for version information

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

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ytsprint.version import (
    AUTHOR,
    AUTHOR_EMAIL,
    CLI_DESCRIPTION,
    LICENSE,
    PROJECT_NAME,
    PROJECT_URL,
    VERSION,
    generate_windows_version_files,
    generate_windows_version_info,
    get_version_for_argparse,
)


class TestVersionInfo(unittest.TestCase):
    """Version information tests"""

    def test_version_format(self):
        """Test version format (should be in X.Y.Z format)"""
        self.assertIsInstance(VERSION, str)
        self.assertRegex(VERSION, r"^\d+\.\d+\.\d+$", f"Version {VERSION} should be in X.Y.Z format")

    def test_author_not_empty(self):
        """Test that author is specified"""
        self.assertIsInstance(AUTHOR, str)
        self.assertGreater(len(AUTHOR.strip()), 0, "Author should not be empty")
        self.assertEqual(AUTHOR, "Sergei Sveshnikov", "Author should be Sergei Sveshnikov")

    def test_license_not_empty(self):
        """Test that license is specified"""
        self.assertIsInstance(LICENSE, str)
        self.assertGreater(len(LICENSE.strip()), 0, "License should not be empty")

    def test_license_is_gpl3(self):
        """Test that license is specified as GPL-3.0"""
        self.assertEqual(LICENSE, "GPL-3.0", "License should be GPL-3.0")

    def test_project_name_not_empty(self):
        """Test that project name is specified"""
        self.assertIsInstance(PROJECT_NAME, str)
        self.assertGreater(len(PROJECT_NAME.strip()), 0, "Project name should not be empty")

    def test_author_email_format(self):
        """Test that author email is valid format"""
        self.assertIsInstance(AUTHOR_EMAIL, str)
        self.assertIn("@", AUTHOR_EMAIL, "Author email should contain @")
        self.assertIn(".", AUTHOR_EMAIL, "Author email should contain .")
        self.assertEqual(AUTHOR_EMAIL, "svesh87@gmail.com", "Author email should be svesh87@gmail.com")

    def test_project_url_format(self):
        """Test that project URL is valid"""
        self.assertIsInstance(PROJECT_URL, str)
        self.assertTrue(PROJECT_URL.startswith("https://"), "Project URL should start with https://")
        self.assertIn("github.com", PROJECT_URL, "Project URL should point to GitHub")
        self.assertEqual(PROJECT_URL, "https://github.com/svesh/yt-sprint-tool/", "Project URL should be correct GitHub URL")

    def test_windows_version_info(self):
        """Test Windows version information generation"""
        win_info = generate_windows_version_info(
            filename="test.exe", description="Test Description", product_name="Test Product"
        )

        self.assertIsInstance(win_info, str)
        self.assertIn("VSVersionInfo", win_info)
        self.assertIn(VERSION.replace(".", ","), win_info)  # Windows version format
        self.assertIn(AUTHOR, win_info)
        self.assertIn(AUTHOR_EMAIL, win_info)
        self.assertIn(PROJECT_URL, win_info)
        self.assertIn("Test Description", win_info)
        self.assertIn("Test Product", win_info)

    def test_argparse_version_format(self):
        """Version flag renders single-line description with metadata."""
        version_str = get_version_for_argparse("ytsprint")

        self.assertNotIn("\n", version_str)
        self.assertIn(PROJECT_NAME, version_str)
        self.assertIn(VERSION, version_str)
        self.assertIn(AUTHOR, version_str)
        self.assertIn(LICENSE, version_str)
        self.assertIn(PROJECT_URL, version_str)
        self.assertIn(CLI_DESCRIPTION, version_str)
        self.assertIn("|", version_str)

    def test_version_contains_gpl_license(self):
        """Version output mentions the GPL license."""
        version_str = get_version_for_argparse("ytsprint")
        self.assertIn("GPL-3.0", version_str)

    def test_generate_windows_version_files(self) -> None:
        """generate_windows_version_files should write artifacts with metadata."""

        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    generate_windows_version_files()

                output = buffer.getvalue()
                self.assertIn("ytsprint_version.py", output)

                version_path = Path(tmpdir) / "ytsprint_version.py"

                self.assertTrue(version_path.exists())

                contents = version_path.read_text(encoding="utf-8")

                self.assertIn(CLI_DESCRIPTION, contents)
                self.assertIn(VERSION.replace(".", ","), contents)
                self.assertIn(AUTHOR_EMAIL, contents)
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
