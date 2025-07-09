"""
llm/overview.py

本模块用于通过大语言模型（LLM）分析视频字幕内容，自动生成视频目录和摘要。

主要功能：
- 读取 .sentences.md 字幕文件，自动过滤无效内容（如 [Music] 等）
- 调用 LLM（如 OpenAI GPT-4o-mini）生成视频目录以及每段 200-300 字的中文摘要

用法：
    from ytx.core.llm import summary as llm_summary
    llm_summary.run(sentence_path)

参数：
    sentence_path: Path，字幕句子文件路径（.sentences.md）

返回：
    string, 视频目录和摘要
"""

import logging
from pathlib import Path
from typing import Dict, Any

from ytx.core.llm.common import call_llm

logger = logging.getLogger(__name__)

def run(sentence_path: Path):
    try:
        sentences = _load_sentences(sentence_path)
        if not sentences:
            logger.warning("没有找到字幕内容")
            return "No valid content found."
        
        # 调用 LLM 生成视频目录和摘要
        logger.info("调用 LLM 生成目录和摘要")
        result = _generate_summary(sentences)
        
        logger.info("LLM 分析完成")
        return result
    except Exception as e:
        logger.error(f"LLM 分析失败: {e}")
        return f"Error occurred: {e}"

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
                    sentence = re.sub(r'\[.*?\]', '', sentence).strip()  # 去除无效标签，如 [Music] 等
                    if sentence:
                        sentences.append(sentence)
        return ' '.join(sentences)  # 返回有效的字幕文本
    except Exception as e:
        logger.error(f"读取字幕文件失败: {e}")
        return ""

def _generate_summary(content: str) -> str:
    prompt = f"""
以下是视频字幕的内容，请根据内容生成视频章节, 章节原则上不超过5个，每个章节的描述尽量详细，说清楚每个章节的关键内容。
最后整理核心观点。

### 字幕内容：
{content}

### 返回格式：
- 章节目录以其对应的内容和核心观点，详细一些
- 不要采用markdown格式，直接输出纯文本


### 示例：
1. AI的演变与未来展望 (00:00 - 00:30)
在这一部分，演讲者讨论了人工智能（AI）在过去一年中的演变及其对各行各业的潜在影响。他指出，AI技术正在迅速发展，并将在未来几年内对各行各业产生深远影响。

2. 广告系统的转型与商业代理 (05:00 - 05:30)
演讲者详细介绍了Meta在广告系统中的AI应用，强调了如何通过自动化来简化广告投放过程。企业只需设定目标和预算，Meta便能提供最佳结果。这种转型被称为“商业结果机器”，预计将显著改变广告行业的运作方式。此外，演讲者还提到未来每个企业都将拥有一个AI代理，用于客户支持和销售，这将极大地提升商业效率。

3. 消息平台与AI的结合 (08:00 - 08:30)
演讲者探讨了在不同国家（如泰国和越南）中，低成本人力劳动如何促进了基于消息的商业模式的发展。他认为，随着AI技术的进步，未来每个企业都将拥有一个AI代理，能够在消息平台上进行客户支持和销售。这种转变将使得企业能够以更低的成本提供高质量的客户服务，进而推动商业的快速增长。

"""


    result = call_llm(prompt, model="gpt-4o-mini", return_raw=True)
    return result
