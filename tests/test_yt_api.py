#!/usr/bin/env python3
"""
Tests for checking functionality of YT Sprint Tool libraries.

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

import unittest
from unittest.mock import MagicMock, patch

from ytsprint import lib_date_utils, lib_yt_api


class TestDateUtils(unittest.TestCase):
    """Tests for lib_date_utils module."""

    def test_parse_year_week(self) -> None:
        """Test week parsing."""
        year, week = lib_date_utils.DateUtils.parse_year_week("2025.32")
        self.assertEqual(year, 2025)
        self.assertEqual(week, 32)

    def test_parse_year_week_invalid(self) -> None:
        """Test week parsing with invalid data."""
        with self.assertRaises(Exception):  # ArgumentTypeError or ValueError
            lib_date_utils.DateUtils.parse_year_week("invalid")

        with self.assertRaises(Exception):  # ArgumentTypeError or ValueError
            lib_date_utils.DateUtils.parse_year_week("2025.60")

    def test_format_sprint_name(self) -> None:
        """Test sprint name formatting."""
        name = lib_date_utils.DateUtils.format_sprint_name(2025, 32)
        self.assertEqual(name, "2025.32 Sprint")

    def test_iso_week_range_utc(self) -> None:
        """Test week range calculation."""
        monday, friday, start_ms, finish_ms = lib_date_utils.DateUtils.iso_week_range_utc(2025, 32)
        self.assertTrue(monday.startswith("2025-08"))
        self.assertTrue(friday.startswith("2025-08"))
        self.assertIsInstance(start_ms, int)
        self.assertIsInstance(finish_ms, int)
        self.assertLess(start_ms, finish_ms)

    def test_get_current_week(self) -> None:
        """Test getting current week."""
        year, week = lib_date_utils.DateUtils.get_current_week()
        self.assertIsInstance(year, int)
        self.assertIsInstance(week, int)
        self.assertGreaterEqual(year, 2020)
        self.assertGreaterEqual(week, 1)
        self.assertLessEqual(week, 53)

    def test_process_week_parameter_current(self) -> None:
        """Test week parameter processing (current)."""
        result = lib_date_utils.DateUtils.process_week_parameter(None)
        year, week, sprint_name, _, _, start_ms, finish_ms = result

        self.assertIsInstance(year, int)
        self.assertIsInstance(week, int)
        self.assertIn("Sprint", sprint_name)
        self.assertIsInstance(start_ms, int)
        self.assertIsInstance(finish_ms, int)

    def test_process_week_parameter_specific(self) -> None:
        """Test week parameter processing (specific)."""
        result = lib_date_utils.DateUtils.process_week_parameter("2025.30")
        year, week, sprint_name, _, _, _, _ = result

        self.assertEqual(year, 2025)
        self.assertEqual(week, 30)
        self.assertEqual(sprint_name, "2025.30 Sprint")


class TestYouTrackAPI(unittest.TestCase):
    """Tests for YouTrackAPI class."""

    def setUp(self) -> None:
        """Test setup."""
        self.api = lib_yt_api.YouTrackAPI("http://test.com", "test-token")

    def test_init(self) -> None:
        """Test API client initialization."""
        self.assertEqual(self.api.base_url, "http://test.com")
        self.assertEqual(self.api.token, "test-token")
        self.assertIn("Authorization", self.api.headers)
        self.assertEqual(self.api.headers["Authorization"], "Bearer test-token")

    def test_init_trailing_slash(self) -> None:
        """Test initialization with URL ending with /."""
        api = lib_yt_api.YouTrackAPI("http://test.com/", "test-token")
        self.assertEqual(api.base_url, "http://test.com")

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_get(self, mock_get):
        """Test GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.api.get("/api/test")
        mock_get.assert_called_once()
        self.assertEqual(result, {"test": "data"})

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_get_with_params(self, mock_get):
        """Test GET request with parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        self.api.get("/api/test", params={"fields": "id,name"})
        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        self.assertIn("params", kwargs)
        self.assertEqual(kwargs["params"], {"fields": "id,name"})

    @patch("ytsprint.lib_yt_api.requests.post")
    def test_post(self, mock_post):
        """Test POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"created": "data"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.api.post("/api/test", {"data": "test"})
        mock_post.assert_called_once()
        self.assertEqual(result, {"created": "data"})

    @patch("ytsprint.lib_yt_api.requests.delete")
    def test_delete_success(self, mock_delete):
        """Test DELETE request (successful)."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        # Should not raise exceptions
        self.api.delete("/api/test")
        mock_delete.assert_called_once()

    @patch("ytsprint.lib_yt_api.requests.delete")
    def test_delete_not_found(self, mock_delete):
        """Test DELETE request (404 - not found)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_delete.return_value = mock_response

        # 404 should not raise exception
        self.api.delete("/api/test")
        mock_delete.assert_called_once()

    @patch("ytsprint.lib_yt_api.requests.delete")
    def test_delete_error_raises(self, mock_delete):
        """Test DELETE request errors propagate via raise_for_status."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("HTTP 500")
        mock_delete.return_value = mock_response

        with self.assertRaises(Exception):
            self.api.delete("/api/test")

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_find_board_id_found(self, mock_get):
        """Test board ID search (found)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "board1", "name": "Test Board"},
            {"id": "board2", "name": "Other Board"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        board_id = self.api.find_board_id("Test Board")
        self.assertEqual(board_id, "board1")

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_find_board_id_not_found(self, mock_get):
        """Test board ID search (not found)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "board1", "name": "Test Board"},
            {"id": "board2", "name": "Other Board"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        board_id = self.api.find_board_id("Non Existent")
        self.assertIsNone(board_id)

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_sprint_exists_true(self, mock_get):
        """Test sprint existence check (exists)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "sprint1", "name": "2025.32 Sprint"},
            {"id": "sprint2", "name": "2025.33 Sprint"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        exists = self.api.sprint_exists("board123", "2025.32 Sprint")
        self.assertTrue(exists)

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_sprint_exists_false(self, mock_get):
        """Test sprint existence check (does not exist)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "sprint1", "name": "2025.33 Sprint"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        exists = self.api.sprint_exists("board123", "2025.32 Sprint")
        self.assertFalse(exists)

    @patch("ytsprint.lib_yt_api.requests.post")
    def test_create_sprint(self, mock_post):
        """Test sprint creation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "sprint123", "name": "Sprint 1"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        sprint_data = {"name": "Sprint 1", "start_ms": 1672531200000, "finish_ms": 1673135999000}
        result = self.api.create_sprint("board123", sprint_data)

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertIn("json", kwargs)
        expected_payload = {"name": "Sprint 1", "start": 1672531200000, "finish": 1673135999000}
        self.assertEqual(kwargs["json"], expected_payload)
        self.assertEqual(result, {"id": "sprint123", "name": "Sprint 1"})

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_find_sprint_id_found(self, mock_get):
        """Test sprint ID search (found)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "sprint1", "name": "2025.32 Sprint"},
            {"id": "sprint2", "name": "2025.33 Sprint"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        sprint_id = self.api.find_sprint_id("board123", "2025.32 Sprint")
        self.assertEqual(sprint_id, "sprint1")

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_find_sprint_id_not_found(self, mock_get):
        """Test sprint ID search (not found)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "sprint1", "name": "2025.33 Sprint"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        sprint_id = self.api.find_sprint_id("board123", "2025.32 Sprint")
        self.assertIsNone(sprint_id)

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_find_project_id_found(self, mock_get):
        """Test project ID search (found)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "proj1", "name": "Test Project"},
            {"id": "proj2", "name": "Other Project"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        project_id = self.api.find_project_id("Test Project")
        self.assertEqual(project_id, "proj1")

    @patch("ytsprint.lib_yt_api.requests.get")
    def test_find_project_id_not_found(self, mock_get):
        """Test project ID search (not found)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "proj1", "name": "Test Project"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        project_id = self.api.find_project_id("Non Existent")
        self.assertIsNone(project_id)

    def test_get_field_defaults(self) -> None:
        """Test getting field defaults wrapper."""
        expected = {"field": {"name": "Sprints"}, "defaultValues": [{"id": "x", "name": "2025.30 Sprint"}]}
        with patch.object(self.api, "get", return_value=expected) as mock_get:
            result = self.api.get_field_defaults("proj", "field")
            self.assertEqual(result, expected)
            mock_get.assert_called_once()

    def test_update_field_default_values_flow(self) -> None:
        """Test full flow of updating defaults (no HTTP errors)."""
        defaults = [{"id": "old1"}, {"id": None}]
        with patch.object(self.api, "get", return_value=defaults) as mock_get, \
            patch.object(self.api, "delete", return_value=204) as mock_delete, \
            patch.object(self.api, "post", return_value=None) as mock_post:
            self.api.update_field_default_values("proj", "field", ["new1", "new2"])
            mock_get.assert_called_once()
            mock_delete.assert_called_once()  # only one valid id
            self.assertEqual(mock_post.call_count, 2)


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def setUp(self) -> None:
        """Setup test data."""
        self.api = lib_yt_api.YouTrackAPI("https://test.myjetbrains.com", "test_token")

    def test_date_utils_and_api_integration(self) -> None:
        """Test DateUtils and YouTrackAPI integration."""
        # Test that data from DateUtils fits API
        _, _, sprint_name, _, _, start_ms, finish_ms = lib_date_utils.DateUtils.process_week_parameter(
            "2025.30"
        )

        # Create sprint_data as in real code
        sprint_data = {"name": sprint_name, "start_ms": start_ms, "finish_ms": finish_ms}

        # Check that data is correct
        self.assertEqual(sprint_data["name"], "2025.30 Sprint")
        self.assertIsInstance(sprint_data["start_ms"], int)
        self.assertIsInstance(sprint_data["finish_ms"], int)
        self.assertLess(sprint_data["start_ms"], sprint_data["finish_ms"])

    def test_get_project_fields(self) -> None:
        """Test getting project fields."""
        mock_fields = [
            {
                "id": "field123",
                "field": {"name": "Sprints"},
                "bundle": {"values": [{"id": "value123", "name": "2025.30 Sprint"}]},
            }
        ]

        with patch.object(self.api, "get", return_value=mock_fields):
            fields = self.api.get_project_fields("proj123")
            self.assertEqual(fields, mock_fields)

    def test_find_bundle_value_by_name(self) -> None:
        """Test searching bundle value by name."""
        bundle_values = [
            {"id": "value123", "name": "2025.30 Sprint"},
            {"id": "value456", "name": "2025.31 Sprint"},
        ]

        # Test found value
        value_id = self.api.find_bundle_value_by_name(bundle_values, "2025.30 Sprint")
        self.assertEqual(value_id, "value123")

        # Test not found value
        value_id = self.api.find_bundle_value_by_name(bundle_values, "Non Existent Sprint")
        self.assertIsNone(value_id)


if __name__ == "__main__":
    # Run tests with more verbose output
    unittest.main(verbosity=2)
