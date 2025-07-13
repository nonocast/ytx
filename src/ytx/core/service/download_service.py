"""
本模块用于下载 YouTube 视频相关资源。

核心职责：
- 读取项目配置文件 project.json
- 下载视频元数据和字幕文件
- 管理下载缓存和强制重新下载
"""

import json
import logging
import os
import re
from typing import Dict, Any
from yt_dlp import YoutubeDL

log = logging.getLogger(__name__)


def run(project_dir: str = ".", force: bool = False):
    project = get_project(project_dir)
    url = project['url']
    download_video(url, project_dir, force)
    download_orig_captions(url, project_dir, force)
    download_zh_captions(url, project_dir, force)
    merge_captions(url, project_dir, force)

def download_video(url: str, project_dir: str = ".", force: bool = False):
    # 获取视频ID
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    video_id = m.group(1) if m else 'video'
    mp4_file = os.path.join(project_dir, f'{video_id}.mp4')
    if os.path.exists(mp4_file):
        log.info(f"⚠️ 视频文件已存在，跳过下载: {mp4_file}")
        return
    try:
        ydl_opts = {
            'quiet': False,
            'outtmpl': mp4_file,
            'merge_output_format': 'mp4',
            'format': (
                'bestvideo[height<=1080][height>=720][ext=mp4][vcodec^=avc1]'
                '+bestaudio[ext=m4a][language^=en]'
                '/best[ext=mp4][vcodec^=avc1]'
            ),
            'noplaylist': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        log.info(f"✅ 视频已保存为 {mp4_file}")
    except Exception as e:
        log.warning(f"❌ 下载视频时出错: {e}")


def get_project(project_dir: str = ".") -> Dict[str, Any]:
    project_path = os.path.join(project_dir, "project.json")
    
    if not os.path.exists(project_path):
        raise FileNotFoundError(f"项目配置文件不存在: {project_path}")
    
    try:
        with open(project_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        return project_data
        
    except json.JSONDecodeError as e:
        log.error(f"项目配置文件 JSON 格式错误: {e}")
        raise
    except Exception as e:
        log.error(f"读取项目配置文件时出错: {e}")
        raise

def download_orig_captions(url: str, project_dir: str = ".", force: bool = False):
    """下载原始语言字幕"""
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    video_id = m.group(1) if m else 'video'
    orig_srt = os.path.join(project_dir, f'{video_id}.orig.srt')
    
    if os.path.exists(orig_srt) and not force:
        log.info(f"⚠️ 原始字幕文件已存在，跳过下载: {orig_srt}")
        return orig_srt
    
    try:
        ydl_opts = {
            'quiet': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en-orig', 'us-orig', 'orig'],
            'outtmpl': os.path.join(project_dir, f'{video_id}.%(ext)s'),
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegSubtitlesConvertor',
                'format': 'srt'
            }]
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 检查是否成功下载了 srt 文件
        for lang in ['en-orig', 'us-orig', 'orig']:
            srt_file = os.path.join(project_dir, f'{video_id}.{lang}.srt')
            if os.path.exists(srt_file):
                # 重命名为统一的文件名
                if srt_file != orig_srt:
                    os.rename(srt_file, orig_srt)
                log.info(f"✅ 原始字幕已保存为 {orig_srt}")
                return orig_srt
        
        log.warning("❌ 未找到原始字幕文件")
        return None
            
    except Exception as e:
        log.warning(f"❌ 下载原始字幕时出错: {e}")
        return None

def download_zh_captions(url: str, project_dir: str = ".", force: bool = False):
    """下载中文字幕"""
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    video_id = m.group(1) if m else 'video'
    zh_srt = os.path.join(project_dir, f'{video_id}.zh.srt')
    
    if os.path.exists(zh_srt) and not force:
        log.info(f"⚠️ 中文字幕文件已存在，跳过下载: {zh_srt}")
        return zh_srt
    
    try:
        ydl_opts = {
            'quiet': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['zh', 'zh-Hans', 'zh-CN'],
            'outtmpl': os.path.join(project_dir, f'{video_id}.%(ext)s'),
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegSubtitlesConvertor',
                'format': 'srt'
            }]
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 检查是否成功下载了 srt 文件
        for lang in ['zh', 'zh-Hans', 'zh-CN']:
            srt_file = os.path.join(project_dir, f'{video_id}.{lang}.srt')
            if os.path.exists(srt_file):
                # 重命名为统一的文件名
                if srt_file != zh_srt:
                    os.rename(srt_file, zh_srt)
                log.info(f"✅ 中文字幕文件已保存为 {zh_srt}")
                return zh_srt
        
        log.warning("❌ 未找到中文字幕文件")
        return None
        
    except Exception as e:
        log.warning(f"❌ 下载中文字幕时出错: {e}")
        return None

def merge_captions(url: str, project_dir: str = ".", force: bool = False):
    """合并原始和中文字幕，生成双语字幕"""
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    video_id = m.group(1) if m else 'video'
    
    orig_srt = os.path.join(project_dir, f'{video_id}.orig.srt')
    zh_srt = os.path.join(project_dir, f'{video_id}.zh.srt')
    merged_srt = os.path.join(project_dir, f'{video_id}.merged.srt')
    
    if os.path.exists(merged_srt) and not force:
        log.info(f"⚠️ 合并字幕文件已存在，跳过合并: {merged_srt}")
        return merged_srt
    
    if not os.path.exists(orig_srt):
        log.warning(f"❌ 原始字幕文件不存在: {orig_srt}")
        return None
    
    if not os.path.exists(zh_srt):
        log.warning(f"❌ 中文字幕文件不存在: {zh_srt}")
        return None
    
    try:
        import pysrt
        
        # 读取字幕文件
        orig_subs = pysrt.open(orig_srt)
        zh_subs = pysrt.open(zh_srt)
        
        # 创建合并字幕列表
        merged_subs = []
        
        # 以原始字幕为基准进行合并
        for i, orig_sub in enumerate(orig_subs):
            merged_sub = pysrt.SubRipItem(
                index=i + 1,
                start=orig_sub.start,
                end=orig_sub.end,
                text=f"{orig_sub.text}\n{zh_subs[i].text if i < len(zh_subs) else ''}"
            )
            merged_subs.append(merged_sub)
        
        # 保存合并字幕
        merged_file = pysrt.SubRipFile(items=merged_subs)
        merged_file.save(merged_srt, encoding='utf-8')
        
        log.info(f"✅ 合并字幕已保存为 {merged_srt}")
        return merged_srt
        
    except Exception as e:
        log.warning(f"❌ 合并字幕时出错: {e}")
        return None
