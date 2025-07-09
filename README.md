# ytx - YouTube 视频分析工具

[![PyPI version](https://img.shields.io/pypi/v/ytx.svg)](https://pypi.python.org/pypi/ytx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ytx 是一个用于 YouTube 视频分析的 Python 工具，支持视频元数据提取、自动字幕下载、LLM 智能分析和项目概览。

## 功能特性

- 🎥 **视频元数据提取**: 自动获取 YouTube 视频的详细信息
- 📝 **自动字幕下载**: 下载并处理视频的自动生成字幕
- 🤖 **LLM 智能分析**: 使用大语言模型分析视频内容，生成摘要和难度评估
- 📊 **项目概览**: 提供美观的视频信息概览，包括播放量、点赞数、语言难度等
- 📁 **项目初始化**: 为视频分析项目创建标准化的目录结构
- 🚀 **命令行界面**: 简单易用的 CLI 工具
- 🎨 **美观输出**: 使用 Rich 库提供彩色终端输出

## 安装

### 从 PyPI 安装

```bash
pip install ytx
```

### 从源码安装

```bash
git clone https://github.com/nonocast/ytx.git
cd ytx
pip install -e .
```

## 使用方法

### 初始化视频项目

```bash
# 基本用法
ytx init https://www.youtube.com/watch?v=VIDEO_ID

# 指定输出目录
ytx init --prefix=my_videos https://www.youtube.com/watch?v=VIDEO_ID

# 强制重新初始化（覆盖现有项目）
ytx init -f --prefix=videos https://www.youtube.com/watch?v=VIDEO_ID
```

### 查看项目概览

```bash
# 查看指定项目的概览
ytx overview videos/VIDEO_ID

# 查看当前目录项目的概览
ytx overview

# 强制重新分析（重新下载字幕和 LLM 分析）
ytx overview --force
```

### 概览信息示例

```
# 🎬 标题：Andrej Karpathy: Software Is Changing (Again)
# 📅 发布：Jun 19, 2025｜⏱️ 时长：39:31｜🌐 Language: English (en-EN)
# 👤 作者：Y Combinator（1.9M subscribers）
# 📊 播放：1,546,421｜👍 44.2K｜💬 960
# 📚 难度：CEFR B2｜语音覆盖：90%｜语速：140 WPM｜句法：中等｜风格：自然｜词汇：标准词汇
# 📝 摘要：在这段演讲中，前特斯拉人工智能主管Andrej Karpathy探讨了软件在人工智能时代的变革...
```

## 项目结构

初始化后的项目目录结构：

```
videos/
└── VIDEO_ID/
    ├── project.json                    # 项目配置文件
    ├── VIDEO_ID.meta.json              # 视频元数据
    ├── VIDEO_ID.en.srt                 # 英语字幕文件
    └── VIDEO_ID.en.sentences.md        # 处理后的字幕句子文件
```

### project.json 示例

```json
{
  "video_id": "74i7daegNZE",
  "url": "https://www.youtube.com/watch?v=74i7daegNZE",
  "lang": "en",
  "created_at": "2024-01-01T12:00:00",
  "assets": {
    "metadata": "74i7daegNZE.meta.json"
  }
}
```

## LLM 分析功能

ytx 集成了大语言模型分析功能，可以：

- **自动生成视频摘要**: 基于字幕内容生成 200-300 字的中文摘要
- **语言难度评估**: 分析 CEFR 等级、语速（WPM）、语音覆盖率等
- **内容风格分析**: 评估句法复杂度、语言风格、词汇特点

### 环境配置

使用 LLM 分析功能需要配置 OpenAI API：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 依赖项

- **typer**: 命令行界面框架
- **rich**: 终端美化输出
- **requests**: HTTP 请求库
- **yt-dlp**: YouTube 视频下载和信息提取
- **openai**: OpenAI API 客户端
- **pysrt**: 字幕文件处理

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
ruff check --fix
```

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 作者

- **nonocast** - *初始工作* - [nonocast](https://github.com/nonocast)

## 更新日志

查看 [HISTORY.rst](HISTORY.rst) 了解版本更新历史。 