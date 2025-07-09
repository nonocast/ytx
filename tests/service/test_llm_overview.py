"""
测试 LLM 概览功能
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

from ytx.core.model.overview_model import Overview
from ytx.core.llm.overview import update, _load_sentences


class TestLLMOverview(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_sentences(self):
        """测试字幕内容加载"""
        # 创建测试字幕文件
        test_content = """[1] 00:00:01 → Hello, welcome to this video.
[2] 00:00:05 → Today we will discuss AI technology.
[3] 00:00:10 → [Music] Let's begin."""
        
        sentence_path = Path(self.temp_dir) / "test.sentences.md"
        with open(sentence_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 测试加载
        result = _load_sentences(sentence_path)
        expected = "Hello, welcome to this video. Today we will discuss AI technology. Let's begin."
        self.assertEqual(result, expected)
    
    @patch('ytx.core.llm.overview.call_llm')
    def test_update_with_llm(self, mock_call_llm):
        """测试 LLM 更新功能"""
        # 模拟 LLM 返回结果
        mock_call_llm.return_value = {
            "summary": "这是一个关于AI技术的视频",
            "difficulty": {
                "cefr": "B2",
                "wpm": 150,
                "voice_coverage": 85,
                "syntax": "中等",
                "style": "自然",
                "vocab": "标准词汇"
            }
        }
        
        # 创建测试字幕文件
        test_content = "[1] 00:00:01 → Hello, welcome to this video."
        sentence_path = Path(self.temp_dir) / "test.sentences.md"
        with open(sentence_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 创建概览对象
        overview = Overview()
        overview.title = "Test Video"
        overview.author = "Test Author"
        overview.duration = "10:00"
        
        # 调用更新函数
        result = update(overview, sentence_path)
        
        # 验证结果
        self.assertEqual(overview.summary, "这是一个关于AI技术的视频")
        self.assertEqual(overview.difficulty["cefr"], "B2")
        self.assertEqual(overview.difficulty["wpm"], 150)
        self.assertEqual(overview.difficulty["voice_coverage"], 85)
        
        # 验证 LLM 被调用
        mock_call_llm.assert_called_once()
    
    def test_update_with_empty_sentences(self):
        """测试空字幕内容的情况"""
        # 创建空的字幕文件
        sentence_path = Path(self.temp_dir) / "empty.sentences.md"
        with open(sentence_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        overview = Overview()
        result = update(overview, sentence_path)
        
        # 应该返回空结果
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main() 