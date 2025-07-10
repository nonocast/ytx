"""
download_service 模块的单元测试
"""

import json
import os
import pytest
from unittest.mock import patch, mock_open
from ytx.core.service.download_service import get_project


class TestGetProject:
    """测试 get_project 函数"""
    
    def test_get_project_success(self, tmp_path):
        """测试成功读取项目配置文件"""
        # 准备测试数据
        project_data = {
            "video_id": "test123",
            "url": "https://www.youtube.com/watch?v=test123",
            "lang": "en",
            "created_at": "2024-01-01T12:00:00",
            "assets": {
                "metadata": "test123.meta.json",
                "captions": "test123.en.srt",
                "sentences": "test123.en.sentences.md"
            }
        }
        
        # 创建临时 project.json 文件
        project_file = tmp_path / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f)
        
        # 切换到临时目录
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # 执行测试
            result = get_project()
            
            # 验证结果
            assert result == project_data
            assert result["video_id"] == "test123"
            assert result["url"] == "https://www.youtube.com/watch?v=test123"
            assert result["lang"] == "en"
            
        finally:
            # 恢复原始目录
            os.chdir(original_cwd)
    
    def test_get_project_file_not_found(self):
        """测试项目配置文件不存在的情况"""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError) as exc_info:
                get_project()
            
            assert "项目配置文件不存在" in str(exc_info.value)
    
    def test_get_project_json_decode_error(self):
        """测试 JSON 格式错误的情况"""
        invalid_json = "{ invalid json content"
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=invalid_json)):
                with pytest.raises(json.JSONDecodeError):
                    get_project()
    
    def test_get_project_io_error(self):
        """测试文件读取错误的情况"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("文件读取失败")):
                with pytest.raises(IOError) as exc_info:
                    get_project()
                
                assert "文件读取失败" in str(exc_info.value) 