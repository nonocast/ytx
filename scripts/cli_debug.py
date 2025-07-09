from ytx.core.service import overview_service
from rich.console import Console

console = Console()

if __name__ == "__main__":
    overview = overview_service.run("videos/74i7daegNZE", force=True)
    print(overview.to_pretty_text())
    # print("-" * 100)
    # overview = overview_service.run("videos/LCEmiRjPEtQ", force=True)
    # print(overview.to_pretty_text())
    # print("-" * 100)
    # overview = overview_service.run("videos/kwpWhRXSwZY", force=True)
    # print(overview.to_pretty_text())
    # print("-" * 100)
    # overview = overview_service.run("videos/tupRbmVM9Wc", force=True)
    # print(overview.to_pretty_text())