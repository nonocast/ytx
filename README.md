# ytx - YouTube 视频分析工具

[![PyPI version](https://img.shields.io/pypi/v/ytx.svg)](https://pypi.python.org/pypi/ytx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ytx 是一个用于 YouTube 视频分析的 Python 工具，支持视频元数据提取、自动字幕检测和项目初始化。

## 功能特性

- 🎥 **视频元数据提取**: 自动获取 YouTube 视频的详细信息
- 📝 **自动字幕检测**: 检测视频是否包含自动生成的字幕
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
ytx overview
```

## 项目结构

初始化后的项目目录结构：

```
videos/
└── VIDEO_ID/
    ├── project.json          # 项目配置文件
    └── VIDEO_ID.meta.json    # 视频元数据
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

## 依赖项

- **typer**: 命令行界面框架
- **rich**: 终端美化输出
- **requests**: HTTP 请求库
- **yt-dlp**: YouTube 视频下载和信息提取

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