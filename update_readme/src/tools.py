"""Custom tools for the Copilot SDK session to update the profile README."""

from __future__ import annotations

import base64
import json
import re
import subprocess
from datetime import UTC
from pathlib import Path

REPOSITORY_SECTION_HEADING = "Here are the repositories I maintain or contribute to:"
TABLE_HEADER = (
    "| Repository | Short Description | Python libraries | Azure services | Data? | AI? |"
)
TABLE_SEPARATOR = (
    "| :--------- | :---------------- | :--------------- | :------------- | :---: | :-: |"
)
FOOTER_TEMPLATE = "_💾 Last saved: {date}_"
TABLE_COLUMNS = 6
_REPO_CELL = re.compile(r"^\[[^\[\]|]+\]\(https://github\.com/[\w.-]+/[\w.-]+\)( ⭐\d+)?$")
_FLAG_VALUES = {"✅", "-"}

# The model exchanges rows in the plain format above; the README shows a decorated
# "high-score" version rendered by ``build_repository_section``.
DISPLAY_HEADER = (
    "| # | Repository | ⭐ | What it does | 🐍 Python libraries | ☁️ Azure services | Tags |"
)
DISPLAY_SEPARATOR = "| :-: | :-- | :-: | :-- | :-- | :-- | :-: |"
DISPLAY_COLUMNS = 7
LEGEND = "<sub>🕹️ High-score table · sorted by stars, then latest push · 📊 data · 🤖 AI</sub>"
DATA_TAG = "📊"
AI_TAG = "🤖"
MEDALS = ("🥇", "🥈", "🥉")
_SEPARATOR_ROW = re.compile(r"^\|(\s*:?-+:?\s*\|)+$")
_REPO_LINK = re.compile(r"^(\[[^\[\]|]+\]\([^)]+\))(?: ⭐(\d+))?$")


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
    """Write the generated repository table while preserving the manual prefix.

    Only the table rows are taken from ``content``; the rest of the generated section
    (heading, table header, footer) is rebuilt so the page layout cannot drift.
    """
    readme_path = Path(repo_path) / "README.md"
    current_content = readme_path.read_text(encoding="utf-8")
    rows = extract_repository_rows(content)
    section = build_repository_section(rows, get_current_date())
    merged_content = preserve_manual_prefix(current_content, section)
    readme_path.write_text(merged_content, encoding="utf-8")
    return f"README.md written successfully ({len(rows)} repositories, {len(merged_content)} chars)"


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


def validate_repository_row(line: str) -> str:
    """Return a normalized table row or raise ``ValueError`` explaining the problem."""
    cells = _cells(line, TABLE_COLUMNS)
    if any(not cell for cell in cells):
        raise ValueError(f"Table cells must not be empty (use '-'): {line!r}")
    if not _REPO_CELL.match(cells[0]):
        msg = f"First cell must be '[name](https://github.com/owner/name)' + optional ⭐N: {line!r}"
        raise ValueError(msg)
    if cells[4] not in _FLAG_VALUES or cells[5] not in _FLAG_VALUES:
        raise ValueError(f"Data?/AI? cells must be '✅' or '-': {line!r}")
    if any(token in line for token in ("<", ">", "`")):
        raise ValueError(f"Table rows must not contain HTML or code: {line!r}")
    return "| " + " | ".join(cells) + " |"


def extract_repository_rows(generated_content: str) -> list[str]:
    """Extract and validate the repository table rows from the model's output."""
    heading_index = generated_content.find(REPOSITORY_SECTION_HEADING)
    if heading_index == -1:
        msg = f"Generated README is missing boundary: {REPOSITORY_SECTION_HEADING!r}"
        raise ValueError(msg)
    lines = generated_content[heading_index:].splitlines()
    try:
        separator_index = next(
            i for i, line in enumerate(lines) if _SEPARATOR_ROW.match(line.strip())
        )
    except StopIteration:
        raise ValueError("Generated README is missing the repository table") from None
    header = lines[separator_index - 1].strip() if separator_index else ""
    if header.startswith("| #"):
        convert = display_row_to_row
    elif header.startswith("| Repository"):
        convert = validate_repository_row
    else:
        raise ValueError("Generated table header must start with '| Repository'")

    rows: list[str] = []
    table_ended = False
    for line in lines[separator_index + 1 :]:
        if not table_ended and line.strip().startswith("|"):
            rows.append(convert(line))
            continue
        table_ended = True
        if "|" in line:
            raise ValueError(f"Table row must start and end with '|': {line!r}")
    if not rows:
        raise ValueError("Generated repository table has no rows")
    seen: set[str] = set()
    for row in rows:
        url = _repo_url(row)
        if url in seen:
            raise ValueError(f"Generated repository table contains duplicate repository: {url}")
        seen.add(url)
    return rows


def _repo_url(row: str) -> str:
    """Return the normalized GitHub URL of a validated plain row."""
    url = row.split("](", 1)[1].split(")", 1)[0]
    return url.lower().rstrip("/").removesuffix(".git")


def _cells(line: str, expected: int) -> list[str]:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        raise ValueError(f"Table row must start and end with '|': {line!r}")
    cells = [cell.strip() for cell in stripped[1:-1].split("|")]
    if len(cells) != expected:
        msg = f"Table row must have {expected} columns (no '|' inside cells): {line!r}"
        raise ValueError(msg)
    return cells


def render_display_row(row: str, position: int) -> str:
    """Decorate a validated plain row for the README high-score table."""
    repo, description, libraries, azure, data, ai = _cells(row, TABLE_COLUMNS)
    match = _REPO_LINK.match(repo)
    if not match:
        raise ValueError(f"Invalid repository cell: {repo!r}")
    link, stars = match.groups()
    rank = MEDALS[position] if position < len(MEDALS) else f"{position + 1:02d}"
    star_cell = stars or "-"
    library_cell = (
        " ".join(f"`{lib.strip()}`" for lib in libraries.split(",")) if libraries != "-" else "-"
    )
    tags = " ".join(tag for tag, on in ((DATA_TAG, data), (AI_TAG, ai)) if on == "✅") or "-"
    cells = [rank, f"**{link}**", star_cell, description, library_cell, azure, tags]
    return "| " + " | ".join(cells) + " |"


def display_row_to_row(line: str) -> str:
    """Convert a decorated README row back into the validated plain format."""
    _rank, repo, stars, description, libraries, azure, tags = _cells(line, DISPLAY_COLUMNS)
    repo = repo.removeprefix("**").removesuffix("**")
    if stars.isdigit():
        repo = f"{repo} ⭐{stars}"
    elif stars != "-":
        raise ValueError(f"Stars cell must be a number or '-': {line!r}")
    if libraries != "-":
        libraries = ", ".join(re.findall(r"`([^`]+)`", libraries)) or libraries
    data = "✅" if DATA_TAG in tags else "-"
    ai = "✅" if AI_TAG in tags else "-"
    return validate_repository_row(
        "| " + " | ".join([repo, description, libraries, azure, data, ai]) + " |"
    )


def build_repository_section(rows: list[str], date: str) -> str:
    """Build the canonical, decorated generated section of the README."""
    body = [render_display_row(row, i) for i, row in enumerate(rows)]
    table = "\n".join([DISPLAY_HEADER, DISPLAY_SEPARATOR, *body])
    footer = FOOTER_TEMPLATE.format(date=date)
    return f"{REPOSITORY_SECTION_HEADING}\n{LEGEND}\n\n{table}\n\n{footer}\n"


def get_current_date() -> str:
    """Return the current date in ISO format."""
    from datetime import datetime

    return datetime.now(UTC).strftime("%Y-%m-%d")
