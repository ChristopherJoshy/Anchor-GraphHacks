# Installation and MCP clients

## Local prerequisites

- Windows 11 with WSL2, macOS, or Linux
- Python 3.12 or 3.13 and `uv`
- Docker Desktop/Engine with Compose v2
- Optional web explorer: Node.js 22.18 or newer and npm

The backend and graph bind to loopback. Verified locally on 18 Oct 2026: Windows 11 build 26200, Python 3.13.14, Docker Desktop 4.95.0 / Engine 29.8.2, and the `falkordb/falkordb:v4.20.4` image. `docker compose ps` showed FalkorDB healthy, `uv run anchor doctor` reported graph and mock ERP ready, and Codex CLI tool calls reached the running MCP endpoint. Claude Code and OpenCode were not exercised.

```powershell
Copy-Item .env.example .env
docker compose up -d
uv sync --extra dev
uv run anchor reset
uv run anchor doctor
uv run anchor serve
```

In a second terminal:

```powershell
uv run pytest
```

MCP: `http://127.0.0.1:8765/mcp`. REST health: `http://127.0.0.1:8765/api/health`. The current Python entry point is `uv run anchor serve`; `anchor reset` replaces the named synthetic graph and SQLite demo state.

### Optional web explorer

Keep the backend running, then use a second terminal:

```powershell
npm --prefix web ci
npm --prefix web run dev
```

Open `http://127.0.0.1:5173`. Build for local preview with `npm --prefix web run build` and `npm --prefix web run preview`. The map uses remote NASA GIBS and OpenStreetMap tiles in addition to bundled Natural Earth overview imagery. See [web-experience.md](web-experience.md) for attribution, privacy, and geographic limitations.

## Codex CLI

The official Codex MCP setup page documents this syntax. Install/register and check discovery:

```powershell
codex mcp add anchor --url http://127.0.0.1:8765/mcp
codex mcp list
```

Codex CLI 0.163.0 is registered to `http://127.0.0.1:8765/mcp`; `codex mcp get anchor` confirmed the URL. A fresh `codex exec` called `anchor_health`, exercised `anchor_modify_dependency` with a deliberately invalid self-link (rejected by validation), and retrieved `anchor_history`. The complete recovery workflow was also run through Codex CLI against the local graph and ERP. Add the server only if it is not already registered; restart Codex if the tool list is stale.

## Claude Code

The current official Claude Code MCP docs show HTTP registration with `--transport http`:

```powershell
claude mcp add --transport http anchor http://127.0.0.1:8765/mcp
claude mcp list
```

In Claude Code, use `/mcp` to check connection and tool availability. This client was not installed/exercised here.

## OpenCode

OpenCode documentation includes remote MCP registration by URL. Check your installed version with `opencode --version`; if it supports this CLI form:

```powershell
opencode mcp add anchor --url http://127.0.0.1:8765/mcp
opencode mcp list
```

The current configuration schema has changed across OpenCode versions. If the CLI form is unavailable, use the version's official MCP documentation and merge (do not replace) the server entry into its existing config. For current v2 schema, the server is nested under `mcp.servers`, with `type: "remote"` and `url`. This client was not installed/exercised here.

## Other MCP-compatible clients

Configure a remote Streamable HTTP server at the URL above. The server has no authentication because it is loopback-only; do not expose it remotely. Client discovery and invocation semantics vary, so verify tool listing before demonstration.

## Stop and clean up

Stop the API with Ctrl+C. Stop FalkorDB with `docker compose down`; this retains the named volume. `docker compose down -v` also deletes the graph's persistent volume and is destructive. Delete `.env` only if you created it and no longer need it. The SQLite database is under `data/` and is ignored by Git.

## Primary client documentation

- [Codex MCP setup](https://developers.openai.com/learn/docs-mcp)
- [Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [OpenCode MCP servers](https://opencode.ai/docs/mcp-servers/)
