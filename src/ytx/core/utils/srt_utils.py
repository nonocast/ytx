from pathlib import Path
import pysrt 
import re
import logging
import json
from yt_dlp import YoutubeDL

log = logging.getLogger(__name__)

def download_en_captions(project_dir: str, force: bool) -> Path:
    # Step 1: 读取 metadata 获取 video_id, url
    meta_path = Path(project_dir) / f"{Path(project_dir).name}.meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata not found: {meta_path}")

    with meta_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    video_id = metadata.get("id") or Path(project_dir).name
    url = metadata.get("webpage_url")
    if not url:
        raise ValueError("Missing 'webpage_url' in metadata.")

    # 专门下载英语字幕
    lang_code = "en"
    final_srt = Path(project_dir) / f"{video_id}.{lang_code}.srt"  # 例如 74i7daegNZE.en.srt

    # Step 2: 检查缓存
    if final_srt.exists() and not force:
        log.info(f"🟡 Captions already cached: {final_srt}")
        return final_srt

    # Step 3: 下载 SRT 自动字幕
    log.info(f"📥 Downloading auto captions for video={video_id}, lang={lang_code}")
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [lang_code],
        "subtitlesformat": "srt",
        "outtmpl": str(Path(project_dir) / f"{video_id}"),
        "quiet": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Step 4: 重命名为 video-id.en-orig.srt
    raw_srt = Path(project_dir) / f"{video_id}.{lang_code}.srt"
    if not raw_srt.exists():
        raise FileNotFoundError(f"Expected subtitle file not found: {raw_srt}")

    raw_srt.rename(final_srt)
    log.info(f"✅ Captions saved as: {final_srt}")
    return final_srt

def generate_sentence_md_from_srt(srt_path: Path) -> Path:
    # 加载 SRT 文件
    subs = pysrt.open(srt_path, encoding='utf-8')

    # 合并字幕文本并记录每段的起始时间
    full_text = ""
    time_marks = []
    for sub in subs:
        clean_text = sub.text.replace('\n', ' ').strip()
        if clean_text:
            if full_text:
                full_text += " "  # 保证中间有空格
            time_marks.append((len(full_text), sub.start.to_time()))
            full_text += clean_text

    # 用正则分句：按英文句末标点加空格断句
    sentence_pattern = r'(?<=[.!?。！？])\s+'
    raw_sentences = re.split(sentence_pattern, full_text)

    # 匹配每个句子对应的时间
    sentences = []
    for idx, sentence in enumerate(raw_sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
        # 查找该句在全文的位置
        start_idx = full_text.find(sentence)
        # 找到最靠前的不超过此位置的时间点
        time_str = "None"
        for offset, t in reversed(time_marks):
            if offset <= start_idx:
                time_str = t.strftime("%H:%M:%S")
                break
        sentences.append((idx + 1, time_str, sentence))

    # 写入 .sentences.md 文件
    out_path = srt_path.with_name(srt_path.stem + ".sentences.md")
    with out_path.open("w", encoding="utf-8") as f:
        for idx, t, s in sentences:
            f.write(f"[{idx}] {t} → {s}\n")

    return out_path
