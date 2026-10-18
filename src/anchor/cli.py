"""Local Anchor operator commands."""

import json

import typer
import uvicorn

from anchor.config import settings
from anchor.graph import GraphUnavailableError
from anchor.service import AnchorService

app = typer.Typer(no_args_is_help=True, help="Anchor synthetic graph recovery agent")


@app.command()
def serve(host: str = settings.host, port: int = settings.port):
    """Start the HTTP API and Streamable HTTP MCP server."""
    uvicorn.run("anchor.app:app", host=host, port=port, reload=False)


@app.command()
def doctor():
    """Check FalkorDB and local mock ERP readiness."""
    try:
        report = AnchorService().health()
    except GraphUnavailableError as exc:
        report = {"ready": False, "mode": "SIMULATION", "error": str(exc)}
    typer.echo(json.dumps(report, indent=2))
    if not report.get("ready"):
        raise typer.Exit(1)


@app.command()
def reset():
    """Reset the deterministic local synthetic demonstration."""
    typer.echo(json.dumps(AnchorService().reset(), indent=2))


if __name__ == "__main__":
    app()
