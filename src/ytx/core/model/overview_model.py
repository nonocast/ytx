'''
# 🎬 标题：How I Moved to New York Alone  
# 📅 发布：Aug 15, 2023｜⏱️ 时长：12:34｜🌐 Language: English (en-US)
# 👤 作者：Emily Vlogs（423K subscribers）  
# 📊 播放：184,230｜👍 8.4K｜💬 423  
# 📝 简介：作者分享搬到纽约一年的变化，从孤独到适应，内容温暖真实，关注情绪、自立和生活节奏，适合喜欢生活类 vlog 的观众。（200～300字）  
# 📚 难度：CEFR B2｜语音覆盖：82% | 语速：135 WPM｜句法：中等｜风格：自然｜词汇：短语丰富，含少量俚语
#
# 英文格式说明：
# - 日期使用英文格式如 Aug 15, 2023
# - 订阅数/点赞数使用英文缩写：K（千），M（百万）
# - 播放数保留完整数字格式，例如 184,230
# - 简介字数控制在 200～300 字（适合 CLI 一次性阅读）
# - 难度信息包括客观（CEFR, WPM）与主观语言特征（语法、风格、词汇）
#
# data structure:
# {
#   "title": "How I Moved to New York Alone",
#   "published_at": "2023-08-15",
#   "duration": "12:34",
#   "author": "Emily Vlogs",
#   "subscribers": 423000,
#   "views": 184230,
#   "likes": 8432,
#   "comments": 423,
#   "summary": "作者分享搬到纽约一年的变化...",
#   "language": { "name": "English", "code": "en-US" },
#   "difficulty": {
#     "cefr": "B2",
#     "voice_coverage": 82,
#     "wpm": 135,
#     "syntax": "中等",
#     "style": "自然",
#     "vocab": "短语丰富，含少量俚语"
#   }
# }

'''
from typing import Dict, Any
from datetime import datetime

class Overview:
    def __init__(
        self,
        title: str = "N/A",
        published_at: str = "N/A",
        duration: str = "N/A",
        author: str = "N/A",
        subscribers: int = 0,
        views: int = 0,
        likes: int = 0,
        comments: int = 0,
        summary: str = "",
        language: Dict[str, str] = None,
        difficulty: Dict[str, Any] = None,
    ):
        self.title = title
        self.published_at = published_at
        self.duration = duration
        self.author = author
        self.subscribers = subscribers
        self.views = views
        self.likes = likes
        self.comments = comments
        self.summary = summary
        self.language = language or {"name": "N/A", "code": "N/A"}
        self.difficulty = difficulty or {
            "cefr": "N/A",
            "voice_coverage": 0,
            "wpm": 0,
            "syntax": "N/A",
            "style": "N/A",
            "vocab": "N/A"
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "published_at": self.published_at,
            "duration": self.duration,
            "author": self.author,
            "subscribers": self.subscribers,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "summary": self.summary,
            "language": self.language,
            "difficulty": self.difficulty,
        }

    def _format_number(self, n: int) -> str:
        if n >= 1_000_000:
            return f"{round(n / 1_000_000, 1)}M"
        elif n >= 1_000:
            return f"{round(n / 1_000, 1)}K"
        return str(n)

    def _format_date(self, date_str: str) -> str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%b %d, %Y")
        except Exception:
            return date_str

    def to_pretty_text(self) -> str:
        return f"""\
# 🎬 标题：{self.title}
# 📅 发布：{self._format_date(self.published_at)}｜⏱️ 时长：{self.duration}｜🌐 Language: {self.language.get("name", "N/A")} ({self.language.get("code", "N/A")})
# 👤 作者：{self.author}（{self._format_number(self.subscribers)} subscribers）
# 📊 播放：{self.views:,}｜👍 {self._format_number(self.likes)}｜💬 {self.comments}
# 📚 难度：CEFR {self.difficulty.get("cefr", "N/A")}｜语音覆盖：{self.difficulty.get("voice_coverage", "N/A")}%｜语速：{self.difficulty.get("wpm", "N/A")} WPM｜句法：{self.difficulty.get("syntax", "N/A")}｜风格：{self.difficulty.get("style", "N/A")}｜词汇：{self.difficulty.get("vocab", "N/A")}
# 📝 摘要：{self.summary}
""".strip()

    def to_table(self):
        from rich.table import Table

        table = Table(title="📊 视频概要", show_lines=True)
        table.add_column("字段", style="cyan")
        table.add_column("内容", style="magenta")

        table.add_row("标题", self.title)
        table.add_row("作者", f"{self.author}（{self._format_number(self.subscribers)} subscribers）")
        table.add_row("发布时间", self._format_date(self.published_at))
        table.add_row("语言", f"{self.language.get('name')} ({self.language.get('code')})")
        table.add_row("时长", self.duration)
        table.add_row("播放量", f"{self.views:,}")
        table.add_row("点赞数", self._format_number(self.likes))
        table.add_row("评论数", str(self.comments))
        table.add_row("CEFR 等级", self.difficulty.get("cefr", "N/A"))
        table.add_row("语音覆盖率", f"{self.difficulty.get('voice_coverage', 'N/A')}%")
        table.add_row("语速 (WPM)", str(self.difficulty.get("wpm", "N/A")))
        table.add_row("句法复杂度", self.difficulty.get("syntax", "N/A"))
        table.add_row("风格", self.difficulty.get("style", "N/A"))
        table.add_row("词汇特点", self.difficulty.get("vocab", "N/A"))
        table.add_row("摘要", self.summary or "（无简介）")

        return table