"""Unit tests for the tools module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.tools import (
    get_current_date,
    list_repos,
    read_current_readme,
    write_readme,
)


class TestReadWriteReadme:
    def test_read_current_readme(self, tmp_path: Path) -> None:
        readme = tmp_path / "README.md"
        readme.write_text("# Hello\nWorld", encoding="utf-8")
        result = read_current_readme(str(tmp_path))
        assert result == "# Hello\nWorld"

    def test_write_readme(self, tmp_path: Path) -> None:
        readme = tmp_path / "README.md"
        readme.write_text("old", encoding="utf-8")
        result = write_readme(str(tmp_path), "# New Content")
        assert "written successfully" in result
        assert readme.read_text(encoding="utf-8") == "# New Content"

    def test_read_missing_readme(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_current_readme(str(tmp_path))


class TestGetCurrentDate:
    def test_returns_iso_date(self) -> None:
        date = get_current_date()
        # Should be YYYY-MM-DD format
        assert len(date) == 10
        assert date[4] == "-"
        assert date[7] == "-"


class TestListRepos:
    @patch("src.tools._gh_graphql")
    def test_filters_private_and_forks(self, mock_graphql: MagicMock) -> None:
        mock_graphql.return_value = {
            "data": {
                "user": {
                    "repositories": {
                        "nodes": [
                            {
                                "name": "public-repo",
                                "url": "https://github.com/user/public-repo",
                                "stargazerCount": 5,
                                "description": "A public repo",
                                "pushedAt": "2026-01-01T00:00:00Z",
                                "primaryLanguage": {"name": "Python"},
                                "isFork": False,
                                "isPrivate": False,
                            },
                            {
                                "name": "private-repo",
                                "url": "https://github.com/user/private-repo",
                                "stargazerCount": 10,
                                "description": "A private repo",
                                "pushedAt": "2026-01-01T00:00:00Z",
                                "primaryLanguage": None,
                                "isFork": False,
                                "isPrivate": True,
                            },
                            {
                                "name": "forked-repo",
                                "url": "https://github.com/user/forked-repo",
                                "stargazerCount": 3,
                                "description": "A fork",
                                "pushedAt": "2026-01-01T00:00:00Z",
                                "primaryLanguage": {"name": "Python"},
                                "isFork": True,
                                "isPrivate": False,
                            },
                        ]
                    }
                }
            }
        }

        result = list_repos("user")
        assert len(result) == 1
        assert result[0]["name"] == "public-repo"
        assert result[0]["stars"] == 5

    @patch("src.tools._gh_graphql")
    def test_sorts_by_stars_then_pushed(self, mock_graphql: MagicMock) -> None:
        mock_graphql.return_value = {
            "data": {
                "user": {
                    "repositories": {
                        "nodes": [
                            {
                                "name": "repo-a",
                                "url": "https://github.com/user/repo-a",
                                "stargazerCount": 0,
                                "description": "Older",
                                "pushedAt": "2025-01-01T00:00:00Z",
                                "primaryLanguage": None,
                                "isFork": False,
                                "isPrivate": False,
                            },
                            {
                                "name": "repo-b",
                                "url": "https://github.com/user/repo-b",
                                "stargazerCount": 0,
                                "description": "Newer",
                                "pushedAt": "2026-01-01T00:00:00Z",
                                "primaryLanguage": None,
                                "isFork": False,
                                "isPrivate": False,
                            },
                            {
                                "name": "repo-c",
                                "url": "https://github.com/user/repo-c",
                                "stargazerCount": 5,
                                "description": "Has stars",
                                "pushedAt": "2024-01-01T00:00:00Z",
                                "primaryLanguage": None,
                                "isFork": False,
                                "isPrivate": False,
                            },
                        ]
                    }
                }
            }
        }

        result = list_repos("user")
        assert len(result) == 3
        # First: repo-c (5 stars)
        assert result[0]["name"] == "repo-c"
        # Second: repo-b (0 stars, newer push)
        assert result[1]["name"] == "repo-b"
        # Third: repo-a (0 stars, older push)
        assert result[2]["name"] == "repo-a"

    @patch("src.tools._gh_graphql")
    def test_excludes_profile_repo(self, mock_graphql: MagicMock) -> None:
        mock_graphql.return_value = {
            "data": {
                "user": {
                    "repositories": {
                        "nodes": [
                            {
                                "name": "user",
                                "url": "https://github.com/user/user",
                                "stargazerCount": 0,
                                "description": "Profile repo",
                                "pushedAt": "2026-01-01T00:00:00Z",
                                "primaryLanguage": None,
                                "isFork": False,
                                "isPrivate": False,
                            },
                        ]
                    }
                }
            }
        }

        result = list_repos("user")
        assert len(result) == 0
