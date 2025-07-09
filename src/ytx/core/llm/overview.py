"""
llm/overview.py

本模块用于通过大语言模型（LLM）分析视频字幕内容，自动生成视频摘要和语言难度评估。

主要功能：
- 读取 .sentences.md 字幕文件，自动过滤无效内容（如 [Music] 等）
- 调用 LLM（如 OpenAI GPT-4o）生成 200-300 字的中文摘要
- 评估语言难度（CEFR、WPM、语音覆盖率、句法、风格、词汇）
- 结果自动写回 Overview 实例

用法：
    from ytx.core.llm import overview as llm_overview
    llm_overview.update(overview, sentence_path)

参数：
    overview: Overview 实例，需先填充基本元数据
    sentence_path: Path，字幕句子文件路径（.sentences.md）

返回：
    dict，包含 LLM 返回的 summary 和 difficulty 字段
"""

import logging
from pathlib import Path
from typing import Dict, Any

from ytx.core.model.overview_model import Overview
from ytx.core.llm.common import call_llm

logger = logging.getLogger(__name__)


def update(overview: Overview, sentence_path: Path):
    try:
        sentences = _load_sentences(sentence_path)
        if not sentences:
            logger.warning("没有找到字幕内容")
            return
        result = _analyze_content_with_llm(overview, sentences)
        _update_overview_from_llm_result(overview, result)
        logger.info("LLM 分析完成")
    except Exception as e:
        logger.error(f"LLM 分析失败: {e}")
        return

def _load_sentences(sentence_path: Path) -> str:
    try:
        with open(sentence_path, 'r', encoding='utf-8') as f:
            content = f.read()
        sentences = []
        for line in content.strip().split('\n'):
            if ' → ' in line:
                sentence = line.split(' → ', 1)[1].strip()
                if sentence:
                    import re
                    sentence = re.sub(r'\[.*?\]', '', sentence).strip()
                    if sentence:
                        sentences.append(sentence)
        return ' '.join(sentences)
    except Exception as e:
        logger.error(f"读取字幕文件失败: {e}")
        return ""


def _analyze_content_with_llm(overview: Overview, sentences: str) -> Dict[str, Any]:
    system_prompt = """你是一个专业的视频内容分析专家。请分析提供的字幕内容，生成以下信息：

1. 视频摘要（summary）：200-300字的中文摘要，描述视频的主要内容和要点
2. 语言难度评估：
   - CEFR等级：A1, A2, B1, B2, C1, C2
   - 语速（WPM）：每分钟单词数
   - 语音覆盖率：基于字幕完整性的百分比
   - 句法复杂度：简单/中等/复杂
   - 风格：正式/自然/学术/口语化等
   - 词汇特点：基础词汇/专业术语/俚语等

请以JSON格式返回结果，格式如下：
{
  "summary": "视频摘要内容",
  "difficulty": {
    "cefr": "B2",
    "wpm": 150,
    "voice_coverage": 85,
    "syntax": "中等",
    "style": "自然",
    "vocab": "标准词汇"
  }
}"""

    user_prompt = f"""请分析以下视频字幕内容：

视频标题：{overview.title}
作者：{overview.author}
时长：{overview.duration}
语言：{overview.language.get('name', 'Unknown')}

字幕内容：
{sentences[:3000]}...

请基于以上信息进行分析。"""

    try:
        result = call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model="gpt-4o-mini",
            temperature=0.3
        )
        return result
    except Exception as e:
        logger.error(f"LLM 调用失败: {e}")
        return {}


def _update_overview_from_llm_result(overview: Overview, result: Dict[str, Any]):
    if result.get("summary"):
        overview.summary = result["summary"]
    difficulty = result.get("difficulty", {})
    if difficulty:
        current_difficulty = overview.difficulty
        if difficulty.get("cefr") and difficulty["cefr"] != "N/A":
            current_difficulty["cefr"] = difficulty["cefr"]
        if difficulty.get("wpm") and difficulty["wpm"] > 0:
            current_difficulty["wpm"] = difficulty["wpm"]
        if difficulty.get("voice_coverage") and difficulty["voice_coverage"] > 0:
            current_difficulty["voice_coverage"] = difficulty["voice_coverage"]
        if difficulty.get("syntax") and difficulty["syntax"] != "N/A":
            current_difficulty["syntax"] = difficulty["syntax"]
        if difficulty.get("style") and difficulty["style"] != "N/A":
            current_difficulty["style"] = difficulty["style"]
        if difficulty.get("vocab") and difficulty["vocab"] != "N/A":
            current_difficulty["vocab"] = difficulty["vocab"]
        overview.difficulty = current_difficulty
