import pytest
from ytx.core.model.overview_model import Overview


@pytest.fixture
def sample_overview_data():
    return {
        "title": "How I Moved to New York Alone",
        "published_at": "2023-08-15",
        "duration": "12:34",
        "author": "Emily Vlogs",
        "subscribers": 423000,
        "views": 184230,
        "likes": 8432,
        "comments": 423,
        "summary": "作者分享搬到纽约一年的变化，从孤独到适应，内容温暖真实。",
        "language": {"name": "English", "code": "en-US"},
        "difficulty": {
            "cefr": "B2",
            "voice_coverage": 82,
            "wpm": 135,
            "syntax": "中等",
            "style": "自然",
            "vocab": "短语丰富，含少量俚语"
        }
    }


@pytest.fixture
def overview_instance(sample_overview_data):
    return Overview(**sample_overview_data)


def test_overview_initialization(overview_instance, sample_overview_data):
    """测试Overview对象初始化"""
    assert overview_instance.title == sample_overview_data["title"]
    assert overview_instance.published_at == sample_overview_data["published_at"]
    assert overview_instance.duration == sample_overview_data["duration"]
    assert overview_instance.author == sample_overview_data["author"]
    assert overview_instance.subscribers == sample_overview_data["subscribers"]
    assert overview_instance.views == sample_overview_data["views"]
    assert overview_instance.likes == sample_overview_data["likes"]
    assert overview_instance.comments == sample_overview_data["comments"]
    assert overview_instance.summary == sample_overview_data["summary"]
    assert overview_instance.language == sample_overview_data["language"]
    assert overview_instance.difficulty == sample_overview_data["difficulty"]


def test_to_dict(overview_instance, sample_overview_data):
    """测试to_dict方法"""
    result = overview_instance.to_dict()
    assert result == sample_overview_data


def test_format_number():
    """测试数字格式化"""
    overview = Overview(
        title="Test",
        published_at="2023-01-01",
        duration="10:00",
        author="Test Author",
        subscribers=1500,
        views=2500000,
        likes=500,
        comments=100,
        summary="Test summary",
        language={"name": "English", "code": "en"},
        difficulty={"cefr": "B1", "voice_coverage": 80, "wpm": 120, "syntax": "简单", "style": "正式", "vocab": "基础"}
    )
    
    # 测试私有方法（通过反射）
    format_number = overview._format_number
    
    assert format_number(500) == "500"
    assert format_number(1500) == "1.5K"
    assert format_number(2500000) == "2.5M"


def test_format_date():
    """测试日期格式化"""
    overview = Overview(
        title="Test",
        published_at="2023-08-15",
        duration="10:00",
        author="Test Author",
        subscribers=1000,
        views=1000,
        likes=100,
        comments=10,
        summary="Test summary",
        language={"name": "English", "code": "en"},
        difficulty={"cefr": "B1", "voice_coverage": 80, "wpm": 120, "syntax": "简单", "style": "正式", "vocab": "基础"}
    )
    
    format_date = overview._format_date
    
    assert format_date("2023-08-15") == "Aug 15, 2023"
    assert format_date("2023-12-25") == "Dec 25, 2023"
    assert format_date("invalid-date") == "invalid-date"


def test_to_pretty_text(overview_instance):
    """测试to_pretty_text方法"""
    result = overview_instance.to_pretty_text()
    
    # 检查关键信息是否包含在输出中
    assert "🎬 标题：How I Moved to New York Alone" in result
    assert "📅 发布：Aug 15, 2023" in result
    assert "⏱️ 时长：12:34" in result
    assert "🌐 Language: English (en-US)" in result
    assert "👤 作者：Emily Vlogs（423.0K subscribers）" in result
    assert "📊 播放：184,230" in result
    assert "👍 8.4K" in result
    assert "💬 423" in result
    assert "📝 简介：作者分享搬到纽约一年的变化" in result
    assert "📚 难度：CEFR B2" in result


def test_to_table(overview_instance):
    """测试to_table方法"""
    table = overview_instance.to_table()
    
    # 检查表格是否创建成功
    assert table is not None
    assert table.title == "📊 视频概要"
    
    # 检查表格行数（实际有15行：标题、作者、发布时间、语言、时长、播放量、点赞数、评论数、CEFR等级、语音覆盖率、语速、句法复杂度、风格、词汇特点、摘要）
    expected_rows = 15
    assert len(table.rows) == expected_rows


def test_overview_with_missing_difficulty():
    """测试缺少difficulty字段的情况"""
    overview = Overview(
        title="Test Video",
        published_at="2023-01-01",
        duration="10:00",
        author="Test Author",
        subscribers=1000,
        views=1000,
        likes=100,
        comments=10,
        summary="Test summary",
        language={"name": "English", "code": "en"},
        difficulty={}  # 空的difficulty
    )
    
    # 测试to_dict
    result = overview.to_dict()
    assert result["difficulty"] == {}
    
    # 测试to_pretty_text中的N/A处理
    text = overview.to_pretty_text()
    assert "CEFR N/A" in text
    assert "语音覆盖：N/A%" in text
    assert "语速：N/A WPM" in text


def test_overview_with_missing_language():
    """测试缺少language字段的情况"""
    overview = Overview(
        title="Test Video",
        published_at="2023-01-01",
        duration="10:00",
        author="Test Author",
        subscribers=1000,
        views=1000,
        likes=100,
        comments=10,
        summary="Test summary",
        language={},  # 空的language
        difficulty={"cefr": "B1", "voice_coverage": 80, "wpm": 120, "syntax": "简单", "style": "正式", "vocab": "基础"}
    )
    
    # 测试to_pretty_text中的N/A处理
    text = overview.to_pretty_text()
    assert "🌐 Language: N/A (N/A)" in text 