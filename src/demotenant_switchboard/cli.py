from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from demotenant_switchboard import __version__
from demotenant_switchboard.services.switchboard import SwitchboardService

app = typer.Typer(no_args_is_help=True, help="Generate resettable SaaS demo tenants from YAML recipes.")


def _service() -> SwitchboardService:
    return SwitchboardService()


@app.command()
def version() -> None:
    """Show the package version."""
    typer.echo(__version__)


@app.command()
def generate(
    recipe: Annotated[Path, typer.Argument(help="Path to a scenario YAML recipe.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output directory.")] = Path("demo-output"),
) -> None:
    """Generate SQLite, JSON, CSV, a demo page, and Playwright tour files."""
    try:
        result = _service().generate(recipe, output)
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps({"output": str(result.output_dir), "checksum": result.checksum}, sort_keys=True))


@app.command()
def validate(
    output: Annotated[Path, typer.Option("--output", "-o", help="Generated output directory.")] = Path("demo-output"),
) -> None:
    """Validate generated files and their SQLite record count."""
    try:
        result = _service().validate(output)
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(result, sort_keys=True))


@app.command()
def reset(
    recipe: Annotated[Path, typer.Argument(help="Path to a scenario YAML recipe.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output directory.")] = Path("demo-output"),
) -> None:
    """Regenerate the scenario so the dataset returns to its initial checksum."""
    result = _service().reset(recipe, output)
    typer.echo(json.dumps({"output": str(result.output_dir), "checksum": result.checksum}, sort_keys=True))


@app.command("switch")
def switch_persona(
    persona: Annotated[str, typer.Argument(help="Persona slug to activate.")],
    output: Annotated[Path, typer.Option("--output", "-o", help="Generated output directory.")] = Path("demo-output"),
) -> None:
    """Write session.json for the selected persona and scoped records."""
    try:
        result = _service().switch_persona(output, persona)
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(result, sort_keys=True))


@app.command()
def tour(
    output: Annotated[Path, typer.Option("--output", "-o", help="Generated output directory.")] = Path("demo-output"),
) -> None:
    """Export a Playwright tour script and markdown step guide."""
    result = _service().export_tour(output)
    typer.echo(json.dumps(result, sort_keys=True))


@app.command()
def checksum(
    output: Annotated[Path, typer.Option("--output", "-o", help="Generated output directory.")] = Path("demo-output"),
) -> None:
    """Print the generated dataset checksum."""
    result = _service().validate(output)
    typer.echo(str(result["checksum"]))


if __name__ == "__main__":
    app()
