import logging
import typer
from rich.console import Console
import ytx.core.service.init_service as init_service
import ytx.core.service.overview_service as overview_service
import ytx.core.service.summary_service as summary_service
import ytx.core.service.download_service as download_service
import ytx.core.service.preview_service as preview_service

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)-8s %(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)
logging.getLogger("ytx.core").setLevel(logging.WARNING)

console = Console()
app = typer.Typer()


"""
ytx init -f --prefix=videos https://www.youtube.com/watch?v=74i7daegNZE
ytx init -f --prefix=videos https://www.youtube.com/watch?v=kwpWhRXSwZY
ytx init -f --prefix=videos https://www.youtube.com/watch?v=LCEmiRjPEtQ
ytx init -f --prefix=videos https://www.youtube.com/watch?v=tupRbmVM9Wc
ytx init -f --prefix=videos https://www.youtube.com/watch?v=MpfWnVbVn2g
"""
@app.command()
def init(
    youtube_url: str, 
    prefix: str = typer.Option(".", help="输出目录前缀"), 
    force: bool = typer.Option(False, "--force", "-f", help="强制重新初始化")
):
    init_service.run(youtube_url, prefix, force)

@app.command()
def overview(
    force: bool = typer.Option(False, "--force", "-f", help="强制重新分析")
):
    overview = overview_service.run(force)
    if overview:
        console.print(overview.to_pretty_text())
    else:
        console.print("[red]无法生成概览信息[/red]")

@app.command()
def summary():
    result = summary_service.run()
    print(result)

@app.command()
def download(force: bool = typer.Option(False, "--force", "-f", help="强制重新下载")):
    download_service.run(force=force)
    print("下载完成")

@app.command()
def preview(force: bool = typer.Option(False, "--force", "-f", help="强制重新生成")):
    preview_service.run(force)
        
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()

if __name__ == "__main__":
    app()
