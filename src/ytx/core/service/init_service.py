"""
init_service.py

本模块用于实现 YouTube 视频项目的初始化服务。

主要职责：
- 从给定的 YouTube 视频链接中提取视频 ID；
- 获取该视频的主语言（即默认字幕语言，如 'en'）；
- 若无可用主语言，则终止并抛出异常，不创建任何目录；
- 若存在主语言，则创建项目目录（如 <video_id>/）；
  并生成 `project.json`，记录视频基本信息及主语言。

设计原则：
- 本模块仅处理业务逻辑，不涉及参数解析或用户交互；
- 错误通过异常抛出，由调用者决定如何提示用户。

示例用法：
    from ytx.core.service import init_service

    init_service.run("https://www.youtube.com/watch?v=74i7daegNZE", ".") -> success
    init_service.run("https://www.youtube.com/watch?v=MpfWnVbVn2g", ".") -> error
"""

import json
import re
from pathlib import Path
from typing import Optional
import requests


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    # Handle different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_video_main_language(video_id: str) -> Optional[str]:
    """
    Get the main language of a YouTube video.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        Main language code (e.g., 'en', 'zh', 'ja') or None if no captions available
        
    Raises:
        ValueError: If video is not accessible or invalid
    """
    try:
        # Get video page to extract caption tracks
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract caption tracks from page
        content = response.text
        
        # Look for caption tracks in the page source
        # This is a simplified approach - in production you might want to use yt-dlp or similar
        caption_pattern = r'"captionTracks":\s*\[(.*?)\]'
        caption_match = re.search(caption_pattern, content, re.DOTALL)
        
        if not caption_match:
            return None
            
        caption_data = caption_match.group(1)
        
        # Extract language codes from caption tracks
        lang_pattern = r'"languageCode":\s*"([^"]+)"'
        languages = re.findall(lang_pattern, caption_data)
        
        if not languages:
            return None
            
        # Return the first language (usually the main/default one)
        return languages[0]
        
    except requests.RequestException as e:
        raise ValueError(f"Failed to access video {video_id}: {e}")
    except Exception as e:
        raise ValueError(f"Error processing video {video_id}: {e}")


def run(url: str, output_dir: str = ".") -> None:
    """
    Initialize a new YouTube project.
    
    Args:
        url: YouTube video URL
        output_dir: Output directory (default: current directory)
    
    Raises:
        FileExistsError: If project already exists
        ValueError: If URL is invalid or video has no captions
    """
    video_id = extract_video_id(url)
    project_dir = Path(output_dir) / video_id
    
    # Check if project already exists
    if project_dir.exists():
        raise FileExistsError(f"Project is already initialized in {project_dir.absolute()}")
    
    # Get video main language
    main_language = get_video_main_language(video_id)
    
    if main_language is None:
        raise ValueError(f"Video {video_id} has no available captions")
    
    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create project.json
    project_data = {
        "video_id": video_id,
        "url": url,
        "main_language": main_language,
        "status": "initialized"
    }
    
    project_file = project_dir / "project.json"
    with open(project_file, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)