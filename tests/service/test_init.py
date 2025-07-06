import tempfile
import json
from pathlib import Path
from unittest.mock import patch, Mock
import pytest
import ytx.core.service.init_service as init_service


def test_extract_video_id():
    """Test video ID extraction from various YouTube URL formats."""
    test_cases = [
        ("https://www.youtube.com/watch?v=74i7daegNZE", "74i7daegNZE"),
        ("https://youtu.be/74i7daegNZE", "74i7daegNZE"),
        ("https://www.youtube.com/embed/74i7daegNZE", "74i7daegNZE"),
        ("https://www.youtube.com/watch?v=74i7daegNZE&t=123s", "74i7daegNZE"),
    ]
    
    for url, expected_id in test_cases:
        assert init_service.extract_video_id(url) == expected_id


def test_extract_video_id_invalid():
    """Test video ID extraction with invalid URLs."""
    invalid_urls = [
        "https://www.youtube.com/",
        "https://example.com/watch?v=123",
        "not a url",
    ]
    
    for url in invalid_urls:
        with pytest.raises(ValueError):
            init_service.extract_video_id(url)


@patch('ytx.core.service.init_service.get_video_main_language')
def test_init_creates_project_json_with_language(mock_get_language):
    """Test successful project initialization with main language."""
    url = "https://www.youtube.com/watch?v=74i7daegNZE"
    video_id = "74i7daegNZE"
    main_language = "en"
    
    mock_get_language.return_value = main_language

    with tempfile.TemporaryDirectory() as tmpdir:
        init_service.run(url, tmpdir)

        project_dir = Path(tmpdir) / video_id
        project_file = project_dir / "project.json"

        assert project_dir.exists()
        assert project_file.exists()

        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        assert project_data["video_id"] == video_id
        assert project_data["url"] == url
        assert project_data["main_language"] == main_language
        assert project_data["status"] == "initialized"


@patch('ytx.core.service.init_service.get_video_main_language')
def test_init_already_exists(mock_get_language):
    """Test that initialization fails if project already exists."""
    url = "https://www.youtube.com/watch?v=74i7daegNZE"
    mock_get_language.return_value = "en"

    with tempfile.TemporaryDirectory() as tmpdir:
        init_service.run(url, tmpdir)
        with pytest.raises(FileExistsError):
            init_service.run(url, tmpdir)


@patch('ytx.core.service.init_service.get_video_main_language')
def test_init_no_captions_available(mock_get_language):
    """Test that initialization fails if video has no captions."""
    url = "https://www.youtube.com/watch?v=MpfWnVbVn2g"
    mock_get_language.return_value = None

    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="has no available captions"):
            init_service.run(url, tmpdir)


@patch('ytx.core.service.init_service.get_video_main_language')
def test_init_network_error(mock_get_language):
    """Test that initialization fails on network errors."""
    url = "https://www.youtube.com/watch?v=invalid"
    mock_get_language.side_effect = ValueError("Failed to access video")

    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="Failed to access video"):
            init_service.run(url, tmpdir)


@patch('requests.get')
def test_get_video_main_language_success(mock_get):
    """Test successful main language detection."""
    video_id = "74i7daegNZE"
    
    # Mock response with caption tracks
    mock_response = Mock()
    mock_response.text = '''
    "captionTracks": [
        {"languageCode": "en", "name": "English"},
        {"languageCode": "zh", "name": "Chinese"}
    ]
    '''
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = init_service.get_video_main_language(video_id)
    assert result == "en"


@patch('requests.get')
def test_get_video_main_language_no_captions(mock_get):
    """Test main language detection when no captions are available."""
    video_id = "MpfWnVbVn2g"
    
    # Mock response without caption tracks
    mock_response = Mock()
    mock_response.text = '{"someOtherData": "value"}'
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = init_service.get_video_main_language(video_id)
    assert result is None


@patch('requests.get')
def test_get_video_main_language_network_error(mock_get):
    """Test main language detection with network errors."""
    video_id = "invalid"
    mock_get.side_effect = Exception("Network error")
    
    with pytest.raises(ValueError, match="Error processing video"):
        init_service.get_video_main_language(video_id)
