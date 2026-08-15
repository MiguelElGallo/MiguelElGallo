"""Custom tools for the Copilot SDK session to update the profile README."""

from __future__ import annotations

import base64
import json
import subprocess
from datetime import UTC
from pathlib import Path

REPOSITORY_SECTION_HEADING = "Here are the repositories I maintain or contribute to:"


def _gh_api(endpoint: str) -> dict | list:
    """Call the GitHub API via the gh CLI."""
    result = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def _gh_graphql(query: str) -> dict:
    """Call the GitHub GraphQL API via the gh CLI."""
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def list_repos(owner: str = "MiguelElGallo") -> list[dict]:
    """List public, non-fork repos sorted by stars desc, pushedAt desc."""
    query = (
        f'{{ user(login: "{owner}") {{'
        " repositories("
        "first: 100, ownerAffiliations: OWNER,"
        " privacy: PUBLIC,"
        " orderBy: {field: STARGAZERS, direction: DESC}"
        ") { nodes {"
        " name url stargazerCount description pushedAt"
        " primaryLanguage { name } isFork isPrivate"
        " } } } }"
    )

    data = _gh_graphql(query)
    repos = data["data"]["user"]["repositories"]["nodes"]

    # Filter: public, non-fork, exclude profile repo
    filtered = [r for r in repos if not r["isPrivate"] and not r["isFork"] and r["name"] != owner]

    # Sort: stars desc, then pushedAt desc (leveraging Python's stable sort)
    filtered.sort(key=lambda r: r["pushedAt"], reverse=True)
    filtered.sort(key=lambda r: -r["stargazerCount"])

    return [
        {
            "name": r["name"],
            "url": r["url"],
            "stars": r["stargazerCount"],
            "description": r["description"] or "",
            "pushed_at": r["pushedAt"],
            "language": r["primaryLanguage"]["name"] if r["primaryLanguage"] else "None",
        }
        for r in filtered
    ]


def get_repo_details(owner: str, repo: str) -> dict:
    """Fetch dependency files (pyproject.toml, requirements.txt) and README for a repo."""
    details: dict[str, str | None] = {
        "repo": repo,
        "readme": None,
        "pyproject_toml": None,
        "requirements_txt": None,
    }

    for filename, key in [
        ("README.md", "readme"),
        ("pyproject.toml", "pyproject_toml"),
        ("requirements.txt", "requirements_txt"),
    ]:
        try:
            resp = _gh_api(f"repos/{owner}/{repo}/contents/{filename}")
            if isinstance(resp, dict) and "content" in resp:
                content = base64.b64decode(resp["content"]).decode("utf-8", errors="replace")
                # Truncate large files to keep context manageable
                details[key] = content[:3000]
        except (subprocess.CalledProcessError, KeyError):
            pass

    return details


def read_current_readme(repo_path: str) -> str:
    """Read the current README.md from the local repo."""
    readme_path = Path(repo_path) / "README.md"
    return readme_path.read_text(encoding="utf-8")


def write_readme(repo_path: str, content: str) -> str:
    """Write the generated repository section while preserving the manual prefix."""
    readme_path = Path(repo_path) / "README.md"
    current_content = readme_path.read_text(encoding="utf-8")
    merged_content = preserve_manual_prefix(current_content, content)
    readme_path.write_text(merged_content, encoding="utf-8")
    return f"README.md written successfully ({len(merged_content)} chars)"


def preserve_manual_prefix(current_content: str, generated_content: str) -> str:
    """Keep all hand-maintained content above the generated repository section."""
    current_heading_index = current_content.find(REPOSITORY_SECTION_HEADING)
    if current_heading_index == -1:
        msg = f"Current README is missing boundary: {REPOSITORY_SECTION_HEADING!r}"
        raise ValueError(msg)

    generated_heading_index = generated_content.find(REPOSITORY_SECTION_HEADING)
    if generated_heading_index == -1:
        msg = f"Generated README is missing boundary: {REPOSITORY_SECTION_HEADING!r}"
        raise ValueError(msg)

    return current_content[:current_heading_index] + generated_content[generated_heading_index:]


def get_current_date() -> str:
    """Return the current date in ISO format."""
    from datetime import datetime

    return datetime.now(UTC).strftime("%Y-%m-%d")
