import os
import json
import logging
from typing import Optional, Literal

from openai import OpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)

# 初始化 OpenAI 客户端（可扩展支持 base_url、自托管等）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 可支持的模型类型（你也可以改成 Enum）
ModelType = Literal["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini", "o4-mini"]


def call_llm(
    prompt: str,
    model: ModelType = "gpt-4o-mini",
    temperature: float = 0.2,
    system_prompt: Optional[str] = None,
    return_raw: bool = False,
    max_tokens: Optional[int] = None,
) -> dict:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        logger.debug(f"Calling OpenAI model: {model}")
        response: ChatCompletion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content.strip()
        if return_raw:
            return content
        return _safe_json_parse(content)
    except Exception as e:
        logger.exception("LLM call failed.")
        raise RuntimeError(f"LLM call failed: {e}")

def _safe_json_parse(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM response as JSON.")
        raise ValueError(f"Invalid JSON output: {content[:200]}...") from e
