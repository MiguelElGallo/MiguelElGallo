"""Unit tests for the tools module."""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.pixel_art import ASSETS_DIR, render_all
from src.tools import (
    REPOSITORY_SECTION_HEADING,
    TABLE_HEADER,
    TABLE_SEPARATOR,
    build_repository_section,
    extract_repository_rows,
    get_current_date,
    list_repos,
    preserve_manual_prefix,
    read_current_readme,
    write_readme,
)

VALID_ROW = "| [demo](https://github.com/user/demo) ⭐3 | Demo tool | typer | - | ✅ | - |"


class TestReadWriteReadme:
    def test_read_current_readme(self, tmp_path: Path) -> None:
        readme = tmp_path / "README.md"
        readme.write_text("# Hello\nWorld", encoding="utf-8")
        result = read_current_readme(str(tmp_path))
        assert result == "# Hello\nWorld"

    def test_write_readme(self, tmp_path: Path) -> None:
        readme = tmp_path / "README.md"
        readme.write_text(
            f"# Profile\n\nManual showcase\n\n{REPOSITORY_SECTION_HEADING}\n\nOld table",
            encoding="utf-8",
        )
        generated = (
            f"# Changed by model\n\n{REPOSITORY_SECTION_HEADING}\n\n"
            f"{TABLE_HEADER}\n{TABLE_SEPARATOR}\n{VALID_ROW}\n\n_Last updated: 1999-01-01_\n"
            "Stray trailing text"
        )
        with patch("src.tools.get_current_date", return_value="2026-01-04"):
            result = write_readme(str(tmp_path), generated)
        assert "written successfully" in result
        assert readme.read_text(encoding="utf-8") == (
            f"# Profile\n\nManual showcase\n\n{REPOSITORY_SECTION_HEADING}\n\n"
            f"{TABLE_HEADER}\n{TABLE_SEPARATOR}\n{VALID_ROW}\n\n_💾 Last saved: 2026-01-04_\n"
        )

    def test_write_readme_rejects_malformed_table_and_keeps_file(self, tmp_path: Path) -> None:
        readme = tmp_path / "README.md"
        original = f"# Profile\n\n{REPOSITORY_SECTION_HEADING}\n\nOld table"
        readme.write_text(original, encoding="utf-8")
        with pytest.raises(ValueError):
            write_readme(str(tmp_path), f"{REPOSITORY_SECTION_HEADING}\n\nNew table")
        assert readme.read_text(encoding="utf-8") == original

    def test_preserve_manual_prefix_rejects_missing_generated_boundary(self) -> None:
        current = f"# Profile\n\n{REPOSITORY_SECTION_HEADING}\n\nOld table"

        with pytest.raises(ValueError, match="Generated README is missing boundary"):
            preserve_manual_prefix(current, "# Profile\n\nReplacement without heading")

    def test_preserve_manual_prefix_rejects_missing_current_boundary(self) -> None:
        generated = f"# Profile\n\n{REPOSITORY_SECTION_HEADING}\n\nNew table"

        with pytest.raises(ValueError, match="Current README is missing boundary"):
            preserve_manual_prefix("# Profile only", generated)

    def test_preserve_manual_prefix_keeps_video_showcase(self) -> None:
        showcase = "## LinkedIn video demos\n\n[Watch video](assets/linkedin-videos/example.mp4)"
        current = f"# Profile\n\n{showcase}\n\n{REPOSITORY_SECTION_HEADING}\n\nOld table"
        generated = f"# Changed\n\n{REPOSITORY_SECTION_HEADING}\n\nNew table"

        result = preserve_manual_prefix(current, generated)

        assert showcase in result
        assert result.endswith(f"{REPOSITORY_SECTION_HEADING}\n\nNew table")

    def test_read_missing_readme(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_current_readme(str(tmp_path))

    def test_profile_video_showcase_assets_are_complete(self) -> None:
        profile_root = Path(__file__).resolve().parents[2]
        readme = (profile_root / "README.md").read_text(encoding="utf-8")
        video_directory = profile_root / "assets" / "linkedin-videos"
        video_names = {
            "agent-plugin-forge",
            "agent-plugin-forge-team-skills",
            "databricks-metric-view",
            "docdr",
            "hellojev",
            "tgrep-codex",
            "tgrep-vscode",
        }

        assert readme.index("LinkedIn video demos") < readme.index(REPOSITORY_SECTION_HEADING)
        assert "raw.githubusercontent.com" not in readme
        for name in video_names:
            assert (video_directory / f"{name}.mp4").is_file()
            assert (video_directory / f"{name}-thumbnail.png").is_file()
            player_url = (
                f"https://miguelelgallo.github.io/MiguelElGallo/assets/linkedin-videos/{name}.mp4"
            )
            assert readme.count(player_url) == 2
            assert f"assets/linkedin-videos/{name}-thumbnail.png" in readme


class TestRepositoryRows:
    def _section(self, *rows: str) -> str:
        return f"{REPOSITORY_SECTION_HEADING}\n\n{TABLE_HEADER}\n{TABLE_SEPARATOR}\n" + "\n".join(
            rows
        )

    def test_normalizes_spacing(self) -> None:
        messy = "|[demo](https://github.com/user/demo) ⭐3|Demo tool| typer |-|✅|-|"
        assert extract_repository_rows(self._section(messy)) == [VALID_ROW]

    @pytest.mark.parametrize(
        ("row", "reason"),
        [
            ("| [demo](https://github.com/user/demo) | a | b | c | ✅ |", "columns"),
            ("| [demo](https://github.com/user/demo) | a | b | c | ✅ | - | x |", "columns"),
            ("| demo | a | b | c | ✅ | - |", "First cell"),
            ("| [demo](https://evil.example/demo) | a | b | c | ✅ | - |", "First cell"),
            ("| [demo](https://github.com/user/demo) | a |  | c | ✅ | - |", "empty"),
            ("| [demo](https://github.com/user/demo) | a | b | c | yes | - |", "Data"),
            ("| [demo](https://github.com/user/demo) | <b>a</b> | b | c | ✅ | - |", "HTML"),
            ("[demo](https://github.com/user/demo) | a | b | c | ✅ | -", "start and end"),
        ],
    )
    def test_rejects_malformed_rows(self, row: str, reason: str) -> None:
        with pytest.raises(ValueError, match=reason):
            extract_repository_rows(self._section(VALID_ROW, row))

    def test_rejects_missing_table_and_duplicates(self) -> None:
        with pytest.raises(ValueError, match="missing the repository table"):
            extract_repository_rows(f"{REPOSITORY_SECTION_HEADING}\n\nno table")
        with pytest.raises(ValueError, match="no rows"):
            extract_repository_rows(self._section())
        with pytest.raises(ValueError, match="duplicate"):
            extract_repository_rows(self._section(VALID_ROW, VALID_ROW))


class TestPublishedReadme:
    """Guards that run in CI before the weekly update is committed."""

    root = Path(__file__).resolve().parents[2]

    def _readme(self) -> str:
        return (self.root / "README.md").read_text(encoding="utf-8")

    def test_generated_section_is_canonical(self) -> None:
        readme = self._readme()
        rows = extract_repository_rows(readme)
        date = readme.rstrip().rsplit("Last saved: ", 1)[1].rstrip("_")
        assert readme.endswith(build_repository_section(rows, date))
        assert len(rows) >= 10

    def test_local_images_exist(self) -> None:
        readme = self._readme()
        paths = re.findall(r'(?:src|srcset)="(assets/[^"]+)"', readme)
        paths += re.findall(r"\]\((assets/[^)]+)\)", readme)
        assert paths
        for path in paths:
            assert (self.root / path).is_file(), path

    def test_eight_bit_artwork_is_wired_up(self) -> None:
        readme = self._readme()
        for name in ("banner", "player-card"):
            assert f'srcset="assets/8bit/{name}-dark.svg"' in readme
            assert f'src="assets/8bit/{name}-light.svg"' in readme
        assert readme.index("banner-light.svg") < readme.index(REPOSITORY_SECTION_HEADING)
        assert readme.count("<picture>") == readme.count("</picture>")
        assert readme.count("<div") == readme.count("</div>")

    def test_pixel_art_is_up_to_date(self) -> None:
        for name, svg in render_all().items():
            assert (ASSETS_DIR / name).read_text(encoding="utf-8") == svg, (
                f"{name} is stale; run `uv run python -m src.pixel_art`"
            )


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
    def test_graphql_query_requests_public_only(self, mock_graphql: MagicMock) -> None:
        """Verify the GraphQL query explicitly requests only public repos."""
        mock_graphql.return_value = {"data": {"user": {"repositories": {"nodes": []}}}}
        list_repos("testuser")
        query_arg = mock_graphql.call_args[0][0]
        assert "privacy: PUBLIC" in query_arg

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
