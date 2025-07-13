"""
init_service.py

本模块用于实现 YouTube 视频分析项目的初始化流程。

核心职责：
- 从给定的 YouTube 视频链接中提取视频 ID；
- 获取该视频的 metadata，并保存为 JSON 文件；
- 判断是否存在自动字幕（automatic captions）；
- 若无字幕，则中止初始化并清理目录；
- 若存在字幕，则生成 project.json。

本模块仅处理业务逻辑，不涉及 CLI 参数解析或终端交互。
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from yt_dlp import YoutubeDL
from rich.console import Console
import logging

console = Console()
log = logging.getLogger(__name__)

def run(url: str, project_dir: str = "videos", force: bool = False):
    # Step 1: 提取视频 ID 和项目路径
    video_id = extract_video_id(url)
    project_path = Path(project_dir) / video_id
    log.debug(f"Target project path: {project_path}")

    # Step 2: 若已存在项目目录，判断是否覆盖
    if project_path.exists() and not force:
        console.print(f"[yellow]⚠️  Project already initialized at[/] [white]{project_path}[/]")
        return

    if project_path.exists() and force:
        shutil.rmtree(project_path)
        log.info(f"Removed existing project at {project_path}")
        console.print(f"[cyan]🗑️  Removed existing project at[/] [white]{project_path}[/]")

    # Step 3: 获取 metadata 并保存
    try:
        metadata = extract_metadata(url)
    except PermissionError as e:
        console.print(f"[red]❌ {e}. Cleaning up.[/]")
        log.warning("403 Forbidden during metadata fetch.")
        if project_path.exists():
            shutil.rmtree(project_path)
        return

    if not metadata:
        console.print("[red]❌ Failed to retrieve video metadata.[/]")
        log.error("yt-dlp failed to extract metadata (not 403).")
        if project_path.exists():
            shutil.rmtree(project_path)
        return

    # Step 4: 检测自动字幕语言
    lang = detect_original_asr_language(metadata)
    if not lang:
        console.print("[red]❌ No original ASR language (auto captions) found. Cleaning up.[/]")
        log.warning("No *-orig caption language detected.")
        if project_path.exists():
            shutil.rmtree(project_path)
        return

    # Step 5: 保存 metadata 并写入 project.json
    project_path.mkdir(parents=True, exist_ok=True)
    metadata_path = project_path / f"{video_id}.meta.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    project_json = {
        "video_id": video_id,
        "title": metadata.get("title", ""),
        "url": url,
        "lang": lang,
        "created_at": timestamp_now(),
        "assets": {
            "metadata": metadata_path.name
        }
    }
    write_project_json(project_path, project_json)
    log.info(f"Project JSON written to {project_path / 'project.json'}")

    # Step 6: 用户反馈
    console.print(f"[bold green]✅ Project initialized at[/] [white]{project_path}[/]")
    console.print(f"[bold blue]🌐 Detected primary language:[/] [white]{lang}[/]")
    console.print(f"[bold yellow]👉 Next: run[/] [white]ytx overview[/] [bold yellow]to analyze and display video info.[/]")


def extract_video_id(url: str) -> str:
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def extract_metadata(url: str) -> Optional[Dict[str, Any]]:
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        if "403" in str(e):
            raise PermissionError("403 Forbidden: YouTube access was denied.")
        return None


def detect_original_asr_language(metadata: dict) -> Optional[str]:
    auto_captions = metadata.get("automatic_captions", {})
    for lang in auto_captions:
        if lang.endswith("-orig"):
            return lang.removesuffix("-orig")
    return None

def write_project_json(project_path: Path, project_data: Dict[str, Any]) -> None:
    project_json_path = project_path / "project.json"
    with open(project_json_path, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)


def timestamp_now() -> str:
    return datetime.now().isoformat()
