# Spiderweb MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/jlowin/fastmcp)

**Spiderweb MCP** is a centralized Model Context Protocol (MCP) gateway designed to bridge **Claude Code** and LLM environments with your personal productivity stack—specifically **Google Workspace (Calendar & Tasks)** and **GitHub**.

Packaged as a lightweight, containerized Python service powered by `FastMCP` and `uv`.

---

## Features

- **Google Calendar Integration:**
  - Dynamic multi-calendar scan (queries primary, family, and shared calendars simultaneously).
  - Chronologically sorted event feeds with human-readable calendar tagging.
  - Robust event creation and deletion with fuzzy calendar name matching and global fallback lookup.
- **Google Tasks Integration:**
  - Full CRUD operations: List, create, complete, and delete tasks.
- **GitHub API Suite:**
  - Browse, create, and comment on Issues.
  - List and open Pull Requests.
  - Direct file commit and branch pushes via PyGithub.
- **Container-First Architecture:**
  - Runs in an isolated Docker container with stdio transport.
  - Zero pollution of host dependencies.

---

## Project Structure

```text
spiderweb-mcp/
├── auth/                 # Persistent OAuth tokens & credentials (gitignored)
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   └── spiderweb_mcp/
│       ├── auth/         # OAuth2 handlers and client factories
│       ├── tools/        # Modular tool definitions (Calendar, Tasks, GitHub, Meta)
│       └── server.py     # FastMCP gateway entry point
├── .env.example
├── pyproject.toml
└── README.md
```

## Quickstart
1. Prerequisites
Docker & Docker Compose

Google Cloud Project with Calendar & Tasks API enabled (OAuth 2.0 Client ID)

GitHub Personal Access Token (classic with repo scope or fine-grained)

2. Configuration
Clone the repository:

Bash
git clone https://github.com/YOUR_USERNAME/spiderweb-mcp.git
cd spiderweb-mcp
Setup environment variables:

Bash
cp .env.example .env
# Edit .env and set your GITHUB_PERSONAL_ACCESS_TOKEN
Place your Google OAuth credentials.json into the auth/ directory:

Bash
mkdir -p auth
cp /path/to/credentials.json auth/credentials.json
Run the one-time OAuth authorization flow:

Bash
# Run directly or inside the virtual environment
uv run python -m spiderweb_mcp.auth.init_oauth

(Follow the terminal link, authorize access, and paste the resulting code to generate auth/token.json).

Running with Docker
Build and run the background container:

Bash
docker compose -f docker/docker-compose.yml up -d --build
Verify that the container is running:

Bash
docker ps --filter "name=runtime_spiderweb-mcp"
Connecting to Claude Code
Add Spidergate directly to Claude Code via standard I/O:

Bash
claude mcp add spiderweb-mcp -- docker exec -i runtime_spiderweb-mcp spiderweb-mcp
Inside Claude Code, run /mcp to verify the connection. All 14 tools will register automatically.

