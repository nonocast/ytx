"""
本模块用于展示 YouTube 视频项目的概览信息。

核心职责：
- 加载指定项目目录下的 project.json；
- 下载字幕文件；
- 提取基础元数据与分析结果字段；
- 基于字幕文件计算语速（WPM）；
- 截断摘要内容至前 10%；
- 返回封装后的 Context 实例，供 CLI 层或其他系统渲染。

说明：
- 本模块只负责业务逻辑，不直接负责终端输出；
- 推荐由上层 CLI 或 UI 层调用 Context.to_table() / to_dict() 展示或导出；
"""

import json
import logging
import os
from typing import Optional, Dict, Any
from rich.console import Console
from ytx.core.model.overview_model import Overview
from ytx.core.utils import srt_utils
from ytx.core.llm import overview as llm_overview

console = Console()
log = logging.getLogger(__name__)

def run(project_dir: str, force: bool = False):
    if not force:
        overview = try_load_overview()
        if overview is not None:
            return overview

    overview = Overview()

    update_overview_meta(project_dir, overview)
    captions_path = srt_utils.download_en_captions(project_dir, force)
    sentence_path = srt_utils.generate_sentence_md_from_srt(captions_path)
    llm_overview.update(overview, sentence_path)
    save_overview(overview)

    return overview

def try_load_overview() -> Optional[Overview]:
    return None

def update_overview_meta(project_dir: str, overview: Overview):
    try:
        # 读取 project.json
        project_path = os.path.join(project_dir, "project.json")
        if not os.path.exists(project_path):
            log.warning(f"项目文件不存在: {project_path}")
            return
            
        with open(project_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # 读取 meta.json
        meta_filename = project_data.get("assets", {}).get("metadata")
        if not meta_filename:
            log.warning("未找到元数据文件名")
            return
            
        meta_path = os.path.join(project_dir, meta_filename)
        if not os.path.exists(meta_path):
            log.warning(f"元数据文件不存在: {meta_path}")
            return
            
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta_data = json.load(f)
        
        # 更新基本元数据
        overview.title = meta_data.get("title", "N/A")
        overview.author = meta_data.get("uploader", "N/A")
        overview.duration = meta_data.get("duration_string", "N/A")
        
        # 处理发布时间
        upload_date = meta_data.get("upload_date")
        if upload_date:
            # 格式: YYYYMMDD -> YYYY-MM-DD
            if len(upload_date) == 8:
                overview.published_at = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            else:
                overview.published_at = upload_date
        else:
            overview.published_at = "N/A"
        
        # 更新统计数据
        overview.views = meta_data.get("view_count", 0)
        overview.likes = meta_data.get("like_count", 0)
        overview.comments = meta_data.get("comment_count", 0)
        overview.subscribers = meta_data.get("channel_follower_count", 0)
        
        # 更新语言信息
        lang_code = project_data.get("lang", "en")
        lang_name_map = {
            "en": "English",
            "zh": "中文",
            "ja": "日本語",
            "ko": "한국어",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "pt": "Português",
            "ru": "Русский"
        }
        overview.language = {
            "name": lang_name_map.get(lang_code, lang_code.upper()),
            "code": f"{lang_code}-{lang_code.upper()}"
        }
        
        # 简介（summary）
        overview.summary = "N/A"
        
        # 难度（difficulty）
        difficulty = {
            "cefr": meta_data.get("cefr", "N/A"),
            "voice_coverage": meta_data.get("voice_coverage", 0),
            "wpm": meta_data.get("wpm", 0),
            "syntax": meta_data.get("syntax", "N/A"),
            "style": meta_data.get("style", "N/A"),
            "vocab": meta_data.get("vocab", "N/A")
        }
        if not any([meta_data.get("cefr"), meta_data.get("voice_coverage"), meta_data.get("wpm"), meta_data.get("syntax"), meta_data.get("style"), meta_data.get("vocab")]):
            difficulty = {
                "cefr": "N/A",
                "voice_coverage": 0,
                "wpm": 0,
                "syntax": "N/A",
                "style": "N/A",
                "vocab": "N/A"
            }
        overview.difficulty = difficulty
        
        log.info(f"成功更新视频元数据: {overview.title}")
        
    except Exception as e:
        log.error(f"更新元数据时出错: {e}")
        console.print(f"[red]错误：无法更新视频元数据 - {e}[/red]")


def save_overview(overview: Overview):
    try:
        overview_data = overview.to_dict()
        overview_path = "overview.json"
        
        with open(overview_path, 'w', encoding='utf-8') as f:
            json.dump(overview_data, f, ensure_ascii=False, indent=2)
        
        log.info(f"成功保存概览数据到: {overview_path}")
        
    except Exception as e:
        log.error(f"保存概览数据时出错: {e}")
        console.print(f"[red]错误：无法保存概览数据 - {e}[/red]")

