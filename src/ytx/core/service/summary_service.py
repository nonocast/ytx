import ytx.core.utils.srt_utils as srt_utils
from ytx.core.llm import summary as llm_summary

def run(project_dir: str, force: bool=False):
    captions_path = srt_utils.download_en_captions(project_dir, force=False)
    sentence_path = srt_utils.generate_sentence_md_from_srt(captions_path)
    result = llm_summary.run(sentence_path)
    return result
