import logging
import typer
from rich.console import Console
from pathlib import Path
import ytx.core.service.init as init_service

logging.basicConfig(level=logging.WARNING)

console = Console()
app = typer.Typer()

@app.command()
def init(youtube_url: str, prefix: str = typer.Option(".", help="输出目录前缀")):
    """Initialize a new YouTube project."""
    try:
        init_service.run(youtube_url, prefix)
    except FileExistsError as e:
        console.print(f"[red]error: {e}[/red]")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def overview():
    """Show project overview."""
    pass
        
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()

if __name__ == "__main__":
    app()
