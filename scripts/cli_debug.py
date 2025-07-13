import ytx.core.service.init_service as init_service
import ytx.core.service.preview_service as preview_service
import ytx.core.service.download_service as download_service
from rich.console import Console
import subprocess
from pathlib import Path

console = Console()

if __name__ == "__main__":
    # target_dir = Path("videos/74i7daegNZE")
    # try:
    #     shutil.rmtree(target_dir)
    # except Exception as e:
    #     print(e)

    # init_service.run("https://www.youtube.com/watch?v=74i7daegNZE", project_dir="videos", force=True)
    # download_service.run(project_dir="videos/74i7daegNZE", force=True)


    preview_service.run("./videos/74i7daegNZE/", force=True)
    try:
        subprocess.run(["open", "./videos/74i7daegNZE/preview.html"], check=True)
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器")

    print("EOF")

