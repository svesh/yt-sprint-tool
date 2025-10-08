#!/usr/bin/env python3
"""
YouTrack API library with common functions.

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

This module contains common functions for working with the YouTrack API,
used by the sprint services and the unified `ytsprint` CLI.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class YouTrackAPI:
    """Class for working with YouTrack API."""

    def __init__(self, base_url: str, token: str) -> None:
        """
        Initialize YouTrack API client.

        Args:
            base_url (str): Base URL of YouTrack.
            token (str): Bearer token for authorization.
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Performs GET request to YouTrack API.

        Args:
            path (str): Path to API endpoint.
            params (dict, optional): Request parameters.

        Returns:
            dict: JSON response from API.

        Raises:
            requests.HTTPError: On HTTP errors.
        """
        url = self.base_url + path
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, payload: Dict[str, Any]) -> Any:
        """
        Performs POST request to YouTrack API.

        Args:
            path (str): Path to API endpoint.
            payload (dict): JSON data to send.

        Returns:
            dict: JSON response from API.

        Raises:
            requests.HTTPError: On HTTP errors.
        """
        url = self.base_url + path
        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def delete(self, path: str) -> int:
        """
        Performs DELETE request to YouTrack API.

        Args:
            path (str): Path to API endpoint.

        Returns:
            int: HTTP status code (200/204/404 considered successful).

        Raises:
            requests.HTTPError: On HTTP errors (except 404).
        """
        url = self.base_url + path
        response = requests.delete(url, headers=self.headers, timeout=30)
        if response.status_code not in (200, 204, 404):
            response.raise_for_status()
        return response.status_code

    def find_board_id(self, board_name: str) -> Optional[str]:
        """
        Finds board ID by name.

        Args:
            board_name (str): Board name.

        Returns:
            str or None: Board ID or None if not found.
        """
        agiles = self.get("/api/agiles", params={"fields": "id,name", "$top": 1000})
        for agile in agiles:
            if agile.get("name") == board_name:
                return agile.get("id")
        return None

    def sprint_exists(self, board_id: str, sprint_name: str) -> bool:
        """
        Checks if sprint with specified name exists.

        Args:
            board_id (str): Board ID.
            sprint_name (str): Sprint name.

        Returns:
            bool: True if sprint exists.
        """
        return self.find_sprint_id(board_id, sprint_name) is not None

    def create_sprint(self, board_id: str, sprint_data: Dict[str, Any]) -> Any:
        """
        Creates new sprint.

        Args:
            board_id (str): Board ID.
            sprint_data (dict): Sprint data with keys:
                - name (str): Sprint name
                - start_ms (int): Start time in UTC milliseconds
                - finish_ms (int): End time in UTC milliseconds

        Returns:
            dict: Created sprint data.
        """
        payload = {
            "name": sprint_data["name"],
            "start": sprint_data["start_ms"],
            "finish": sprint_data["finish_ms"]
        }
        return self.post(f"/api/agiles/{board_id}/sprints", payload)

    def find_sprint_id(self, board_id: str, sprint_name: str) -> Optional[str]:
        """
        Finds sprint ID by name.

        Args:
            board_id (str): Board ID.
            sprint_name (str): Sprint name.

        Returns:
            str or None: Sprint ID or None if not found.
        """
        sprints = self.get(
            f"/api/agiles/{board_id}/sprints",
            params={"fields": "id,name", "$top": 1000},
        )
        for sprint in sprints:
            if sprint.get("name") == sprint_name:
                return sprint.get("id")
        return None

    def find_project_id(self, project_name: str) -> Optional[str]:
        """
        Finds project ID by name.

        Args:
            project_name (str): Project name.

        Returns:
            str or None: Project ID or None if not found.
        """
        projects = self.get(
            "/api/admin/projects",
            params={"fields": "id,name", "$top": 1000},
        )
        for project in projects:
            if project.get("name") == project_name:
                return project.get("id")
        return None

    def update_field_default_values(self, project_id: str, field_id: str, value_ids: List[str]) -> None:
        """
        Update default values for the project field idempotently.

        - If current defaults already match the desired set, do nothing.
        - Remove only defaults that are not desired anymore.
        - Add only defaults that are missing.

        Args:
            project_id (str): Project ID.
            field_id (str): Field ID.
            value_ids (list): List of value IDs that must remain as defaults.
        """
        defaults_path = f"/api/admin/projects/{project_id}/customFields/{field_id}/defaultValues"

        logger.info("Fetching current default values: project=%s field=%s", project_id, field_id)
        defaults = self.get(defaults_path, params={"fields": "id", "$top": 1000})

        current_ids = {d.get("id") for d in defaults if d.get("id")}
        desired_ids = set(value_ids)

        to_remove = current_ids - desired_ids
        to_add = desired_ids - current_ids

        if not to_remove and not to_add:
            logger.info("Defaults already up-to-date; no changes needed")
            return

        if to_remove:
            logger.info("Removing %d default value(s): %s", len(to_remove), ",".join(sorted(to_remove)))
            for default_id in sorted(to_remove):
                status = self.delete(f"{defaults_path}/{default_id}")
                if status == 404:
                    logger.info("Default value already absent: id=%s", default_id)
                else:
                    logger.info("Default value removed: id=%s status=%s", default_id, status)

        if to_add:
            logger.info("Adding %d default value(s): %s", len(to_add), ",".join(sorted(to_add)))
            for value_id in sorted(to_add):
                self.post(defaults_path, {"id": value_id, "$type": "VersionBundleElement"})

        logger.info("Default values update completed: project=%s field=%s", project_id, field_id)

    def get_field_defaults(self, project_id: str, field_id: str) -> Any:
        """
        Gets current default values for field.

        Args:
            project_id (str): Project ID.
            field_id (str): Field ID.

        Returns:
            dict: Information about field and its default values.
        """
        path = f"/api/admin/projects/{project_id}/customFields/{field_id}"
        params = {"fields": "field(name),defaultValues(id,name)", "$top": 10}
        return self.get(path, params=params)

    def get_project_fields(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Gets project fields with bundle values.

        Args:
            project_id (str): Project ID.

        Returns:
            list: List of project fields with bundle data.
        """
        return self.get(
            f"/api/admin/projects/{project_id}/customFields",
            params={"fields": "id,field(id,name),bundle(id,values(id,name)),defaultValues(id,name)"},
        )

    def find_bundle_value_by_name(self, bundle_values: List[Dict[str, Any]], value_name: str) -> Optional[str]:
        """
        Finds value ID in bundle by name.

        Args:
            bundle_values (list): List of bundle values.
            value_name (str): Name of the value to find.

        Returns:
            str or None: Value ID or None if not found.
        """
        for value in bundle_values:
            if value.get("name") == value_name:
                return value.get("id")
        return None
