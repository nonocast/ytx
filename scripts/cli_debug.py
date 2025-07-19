import ytx.core.service.init_service as init_service
import ytx.core.service.preview_service as preview_service
import ytx.core.service.download_service as download_service
import ytx.core.service.overview_service as overview_service
import ytx.core.service.summary_service as summary_service
from rich.console import Console
import subprocess
from pathlib import Path
import logging
import shutil

console = Console()

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)-8s %(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S"
)
logging.getLogger("ytx.core").setLevel(logging.DEBUG)

def clean_project(project_dir: str):
    target_dir = Path(project_dir)
    try:
        shutil.rmtree(target_dir)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    video_id = "74i7daegNZE"

    # clean
    # clean_project(f"videos/{video_id}")

    # init
    # init_service.run(f"https://www.youtube.com/watch?v={video_id}", project_dir="videos", force=True)

    # overview
    # overview = overview_service.run(project_dir=f"videos/{video_id}", force=True)
    # console.print(overview.to_pretty_text())

    # summary
    # summary = summary_service.run(project_dir=f"videos/{video_id}")
    # console.print(summary)

    # download
    # download_service.run(project_dir=f"videos/{video_id}", force=True)

    preview_service.run(f"./videos/{video_id}", force=False)
    try:
        subprocess.run(["open", "./videos/74i7daegNZE/preview.html"], check=True)
        pass
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器")

    print("EOF")


