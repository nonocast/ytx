import os
import json
import logging
import re
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from jinja2 import Environment, FileSystemLoader
from ytx.core.utils import json3_utils

console = Console()
log = logging.getLogger(__name__)

def run(project_dir: str = ".", force: bool = False):
    project = try_load_project(project_dir)
    captions_path = json3_utils.download_en_captions(project_dir, force)
    sentences_path = json3_utils.generate_sentence_md_from_json3(captions_path)
    sentences = parse_sentences_md(sentences_path)
    render(project_dir, project, sentences)


def render(project_dir: str, project: dict, sentences: List[Dict]):
    template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("preview.html.j2")

    html = template.render(
        title=project.get("title"),
        video_path=f"{project.get('video_id')}.mp4",
        sentences=sentences
    )

    output_path = os.path.join(project_dir, "preview.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    console.print(f"[green]✅ 成功生成预览页面:[/] {output_path}")


def try_load_project(project_dir: str) -> dict:
    project_file = os.path.join(project_dir, "project.json")

    if not os.path.exists(project_file):
        raise FileNotFoundError(f"❌ 未找到 {project_file}")

    with open(project_file, "r", encoding="utf-8") as f:
        project = json.load(f)

    return project


def pad_time(t: str) -> str:
    # 保留毫秒部分，主时间部分补零
    if '.' in t:
        main, ms = t.split('.', 1)
        parts = main.split(":")
        parts = [p.zfill(2) for p in parts]
        while len(parts) < 3:
            parts.insert(0, "00")
        return ":".join(parts) + "." + ms
    else:
        parts = t.split(":")
        parts = [p.zfill(2) for p in parts]
        while len(parts) < 3:
            parts.insert(0, "00")
        return ":".join(parts)

def parse_sentences_md(md_path: Path) -> List[Dict]:
    sentences = []
    # 支持毫秒的时间格式
    pattern = re.compile(r"\[(\d+)\] (\d{1,2}:\d{2}:\d{2}(?:\.\d{1,6})?) → (\d{1,2}:\d{2}:\d{2}(?:\.\d{1,6})?) (.+)")

    with md_path.open("r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                sentence_id = int(match.group(1))
                start = pad_time(match.group(2))
                end = pad_time(match.group(3))
                text = match.group(4)
                sentences.append({
                    "id": sentence_id,
                    "start": start,
                    "end": end,
                    "text": text
                })
    return sentences