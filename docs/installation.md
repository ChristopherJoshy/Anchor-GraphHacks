# Installation and MCP clients

## Local prerequisites

- Windows 11 with WSL2, macOS, or Linux
- Python 3.12 or 3.13 and `uv`
- Docker Desktop/Engine with Compose v2
- Optional dashboard: Node.js/npm

The backend and graph bind to loopback. This environment confirmed Python 3.13 and `uv`, but its execution shell could not locate the user's Docker CLI; no container run is claimed.

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

## Codex CLI

The official Codex MCP setup page documents this syntax. Install/register and check discovery:

```powershell
codex mcp add anchor --url http://127.0.0.1:8765/mcp
codex mcp list
```

This command manages Codex's MCP config; it does not overwrite unrelated configuration. Anchor was not registered with Codex in this environment.

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
