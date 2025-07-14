from pathlib import Path
import re
import logging
import json
import html
from yt_dlp import YoutubeDL
from datetime import timedelta

log = logging.getLogger(__name__)

def download_en_captions(project_dir: str, force: bool = False) -> Path:
    project_path = Path(project_dir) / "project.json"
    if project_path.exists():
        with project_path.open("r", encoding="utf-8") as f:
            project_data = json.load(f)
        meta_filename = project_data.get("assets", {}).get("metadata")
        if not meta_filename:
            raise FileNotFoundError(f"project.json 中未找到 assets.metadata 字段: {project_path}")
        meta_path = Path(project_dir) / meta_filename
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata not found: {meta_path}")

    with meta_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    video_id = metadata.get("id") or Path(project_dir).name
    url = metadata.get("webpage_url")
    if not url:
        raise ValueError("Missing 'webpage_url' in metadata.")

    lang_code = "en"
    final_json3 = Path(project_dir) / f"{video_id}.{lang_code}.json3"

    if final_json3.exists() and not force:
        log.info(f"🟡 Captions already cached: {final_json3}")
        return final_json3

    log.info(f"📥 Downloading auto captions for video={video_id}, lang={lang_code}, format=json3")
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [lang_code],
        "subtitlesformat": "json3",
        "outtmpl": str(Path(project_dir) / f"{video_id}"),
        "quiet": True,
        "socket_timeout": 10,
        "retries": 1,
        "nocheckcertificate": True
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    raw_json3 = Path(project_dir) / f"{video_id}.{lang_code}.json3"
    if not raw_json3.exists():
        raise FileNotFoundError(f"Expected subtitle file not found: {raw_json3}")

    raw_json3.rename(final_json3)
    log.info(f"✅ Captions saved as: {final_json3}")
    return final_json3

def format_time(ms: int) -> str:
    """格式化时间为 hh:mm:ss.ffffff"""
    td = timedelta(milliseconds=ms)
    total_seconds = int(td.total_seconds())
    micros = int((td.total_seconds() - total_seconds) * 1_000_000)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h}:{m:02}:{s:02}.{micros:06}"

def generate_sentence_md_from_json3(captions_path: Path) -> Path:
    """基于 json3 中 segs 的 tOffsetMs 精确提取句子及时间范围，输出为 markdown"""
    with captions_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    events = data.get("events", [])
    tokens = []  # (text, abs_time)

    for event in events:
        if "segs" not in event or "tStartMs" not in event:
            continue
        base_time = int(event["tStartMs"])
        for seg in event["segs"]:
            text = html.unescape(seg.get("utf8", "")).strip()
            if not text or re.fullmatch(r"\[.*?\]", text):  # 去掉 [Music] 等
                continue
            offset = int(seg.get("tOffsetMs", 0))
            abs_time = base_time + offset
            tokens.append((text, abs_time))

    # 构建 full_text 和时间映射
    full_text = ""
    time_map = []  # (char_start_index, token_text, time_ms)
    for text, time_ms in tokens:
        if full_text:
            full_text += " "
        start_idx = len(full_text)
        full_text += text
        time_map.append((start_idx, text, time_ms))

    # 分句
    sentence_pattern = r'(?<=[.!?])\s+'
    raw_sentences = re.split(sentence_pattern, full_text)

    sentences = []
    for idx, raw in enumerate(raw_sentences):
        sentence = raw.strip()
        if not sentence:
            continue

        sent_start = full_text.find(sentence)
        tokens_in_sentence = []

        for i, (char_idx, token_text, time_ms) in enumerate(time_map):
            if sent_start <= char_idx < sent_start + len(sentence):
                tokens_in_sentence.append((token_text, time_ms, i))

        if not tokens_in_sentence:
            continue

        first_token_time = tokens_in_sentence[0][1]
        last_token_time = tokens_in_sentence[-1][1]
        last_token_index = tokens_in_sentence[-1][2]

        # 尾音最多延迟 400ms，不超过下一个 token 的时间
        if last_token_index + 1 < len(time_map):
            next_token_time = time_map[last_token_index + 1][2]
            end_time_ms = min(last_token_time + 400, next_token_time)
        else:
            end_time_ms = last_token_time + 400
        
        # 我的调整
        first_token_time = first_token_time - 50
        end_time_ms = last_token_time + 200

        t_start = format_time(first_token_time)
        t_end = format_time(end_time_ms)
        sentences.append((idx + 1, t_start, t_end, sentence))

    # 写入 markdown
    out_path = captions_path.with_name(captions_path.stem + ".precise.sentences.md")
    with out_path.open("w", encoding="utf-8") as f:
        for idx, t_start, t_end, text in sentences:
            f.write(f"[{idx}] {t_start} → {t_end} {text}\n")

    return out_path