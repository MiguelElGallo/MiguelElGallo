"""Main entry point: uses the Copilot SDK to update the profile README."""

from __future__ import annotations

import asyncio
import os
import sys

from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType
from copilot.tools import define_tool
from pydantic import BaseModel, Field

from src.tools import (
    get_current_date,
    get_repo_details,
    list_repos,
    read_current_readme,
    write_readme,
)

REPO_PATH = os.environ.get(
    "REPO_PATH",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
# Go up one more level since we're in update_readme/
if REPO_PATH.endswith("update_readme"):
    REPO_PATH = os.path.dirname(REPO_PATH)

OWNER = os.environ.get("GITHUB_OWNER", "MiguelElGallo")

SYSTEM_PROMPT = """\
You are an assistant that updates a GitHub profile README.md.

Your job:
1. Call `list_repos` to get all public non-fork repositories,
   already sorted by stars desc then last commit date desc.
2. Call `get_repo_details` for EACH repository to inspect its
   dependencies (pyproject.toml, requirements.txt) and README.
3. Call `read_current_readme` to get the current README.md.
4. Based on all the gathered information, produce an UPDATED README.md:
   - Keep the intro paragraph (before "Here are the repositories")
     EXACTLY as-is, do NOT change it.
   - Update the repository table with:
     - Correct ordering (stars desc, then last commit date desc)
     - Star counts as ⭐N (only for repos with stars > 0)
     - Python libraries from pyproject.toml or requirements.txt
     - Azure services from dependencies and README content
     - Data? ✅ if data-related (databases, warehouses, BI,
       reporting, data modeling, ETL/ELT, parquet, arrow)
     - AI? ✅ if AI-related (LLMs, RAG, embeddings, agents,
       ML, OpenAI)
   - Add at the end: `_Last updated: YYYY-MM-DD_` via `get_current_date`
5. Call `write_readme` with the complete updated README.md content.

Table format (markdown):
| Repository | Python libraries | Azure services | Data? | AI? |
| :--------- | :--------------- | :------------- | :---: | :-: |
| [name](url) ⭐N | lib1, lib2 | Service1, Service2 | ✅ | - |

IMPORTANT: Process ALL repos from list_repos, do NOT skip any.
IMPORTANT: Keep the intro paragraph UNCHANGED.
IMPORTANT: Use - (dash) for columns with no value.
"""


# -- Tool parameter models --


class ListReposParams(BaseModel):
    """Parameters for listing repositories."""

    owner: str = Field(default="MiguelElGallo", description="GitHub username")


class GetRepoDetailsParams(BaseModel):
    """Parameters for getting repo details."""

    owner: str = Field(default="MiguelElGallo", description="GitHub username")
    repo: str = Field(description="Repository name")


class ReadReadmeParams(BaseModel):
    """Parameters for reading the README."""

    repo_path: str = Field(default="", description="Path to the repo (leave empty for default)")


class WriteReadmeParams(BaseModel):
    """Parameters for writing the README."""

    repo_path: str = Field(default="", description="Path to the repo (leave empty for default)")
    content: str = Field(description="Full README.md content to write")


# -- Tool definitions --


@define_tool(description="List all public non-fork repos, sorted by stars then last commit")
async def tool_list_repos(params: ListReposParams) -> list[dict]:
    return list_repos(params.owner)


@define_tool(
    description="Fetch dependency files and README to determine Python libs and Azure services"
)
async def tool_get_repo_details(params: GetRepoDetailsParams) -> dict:
    return get_repo_details(params.owner, params.repo)


@define_tool(description="Read the current README.md from the local repository")
async def tool_read_readme(params: ReadReadmeParams) -> str:
    path = params.repo_path or REPO_PATH
    return read_current_readme(path)


@define_tool(description="Write the updated README.md to the local repository")
async def tool_write_readme(params: WriteReadmeParams) -> str:
    path = params.repo_path or REPO_PATH
    return write_readme(path, params.content)


class GetDateParams(BaseModel):
    """No parameters needed."""

    pass


@define_tool(description="Get today's date in YYYY-MM-DD format (UTC)")
async def tool_get_date(params: GetDateParams) -> str:
    return get_current_date()


async def main() -> None:
    """Run the Copilot SDK session to update the README."""
    print("🚀 Starting Copilot SDK session to update README...")

    client = CopilotClient()
    await client.start()

    session = await client.create_session(
        {
            "model": "claude-sonnet-4",
            "streaming": True,
            "system_message": {"content": SYSTEM_PROMPT},
            "tools": [
                tool_list_repos,
                tool_get_repo_details,
                tool_read_readme,
                tool_write_readme,
                tool_get_date,
            ],
        }
    )

    # Track progress via events
    done = asyncio.Event()

    def handle_event(event):
        t = event.type
        d = event.data

        if t == SessionEventType.SESSION_START:
            print("📡 Session started")
        elif t == SessionEventType.ASSISTANT_TURN_START:
            print("\n🤖 Agent thinking...")
        elif t == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(d.delta_content or "")
            sys.stdout.flush()
        elif t == SessionEventType.ASSISTANT_MESSAGE:
            print()  # newline after streamed message
        elif t == SessionEventType.TOOL_EXECUTION_START:
            tool = d.tool_name or "unknown"
            args = d.arguments or ""
            # Truncate long args for readability
            args_str = str(args)
            if len(args_str) > 200:
                args_str = args_str[:200] + "..."
            print(f"\n🔧 Calling tool: {tool}({args_str})")
        elif t == SessionEventType.TOOL_EXECUTION_COMPLETE:
            tool = d.tool_name or "unknown"
            result = str(d.result or "")
            if len(result) > 300:
                result = result[:300] + "..."
            print(f"  ✅ {tool} → {result}")
        elif t == SessionEventType.TOOL_EXECUTION_PROGRESS:
            msg = d.progress_message or ""
            if msg:
                print(f"  ⏳ {msg}")
        elif t == SessionEventType.ASSISTANT_TURN_END:
            print("🏁 Agent turn complete")
        elif t == SessionEventType.ASSISTANT_USAGE:
            in_tok = getattr(d, "input_tokens", None)
            out_tok = getattr(d, "output_tokens", None)
            model = getattr(d, "model", None)
            parts = []
            if model:
                parts.append(f"model={model}")
            if in_tok is not None:
                parts.append(f"in={in_tok}")
            if out_tok is not None:
                parts.append(f"out={out_tok}")
            if parts:
                print(f"  📊 Usage: {', '.join(parts)}")
        elif t == SessionEventType.SESSION_ERROR:
            err = getattr(d, "error", None) or d
            print(f"\n❌ Error: {err}")
        elif t == SessionEventType.SESSION_IDLE:
            print()
            done.set()

    session.on(handle_event)

    await session.send_and_wait(
        {
            "prompt": (
                f"Please update the README.md for {OWNER}'s GitHub profile. "
                "Follow the system instructions precisely. "
                "Start by listing repos, then get details for each, "
                "read the current README, and finally write the updated version."
            ),
        },
        timeout=600.0,
    )

    print("✅ README update complete!")
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
