import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path to allow module imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from publishers.wechat_publisher import WeChatPublisher

@pytest.fixture
def mock_config():
    """Fixture for mock configuration."""
    return {
        'app_id': 'test_app_id',
        'app_secret': 'test_app_secret',
        'author': '默认作者',
    }

@pytest.fixture
def publisher(mock_config):
    """Fixture for WeChatPublisher instance."""
    return WeChatPublisher(config=mock_config, account_name='test_account')


def test_publish_success(publisher, tmp_path):
    """Test the entire publish process with mocks for external APIs."""
    # Create a dummy article file and image file for the test
    fixtures_dir = tmp_path / "fixtures"
    fixtures_dir.mkdir()
    article_path = fixtures_dir / "test_article.md"
    article_path.write_text(
        """---
title: '测试文章'
author: '测试作者'
---

# 测试标题

内容部分。

![图片](image.png)
""", encoding='utf-8'
    )
    image_path = fixtures_dir / "image.png"
    image_path.touch()

    # Mock the external API calls at a higher level
    with patch.object(publisher, 'upload_image', return_value='http://mock.url/image.png') as mock_upload_image:
        with patch.object(publisher, '_upload_thumb_image', return_value='mock_thumb_media_id') as mock_upload_thumb:
            with patch.object(publisher, '_create_draft', return_value=True) as mock_create_draft:
                # Call the publish method
                success = publisher.publish(str(article_path))

                # Assertions
                assert success is True

                # Verify that the correct methods were called with the right arguments
                mock_upload_image.assert_called_once_with(str(image_path))
                mock_upload_thumb.assert_called_once_with(str(image_path))
                mock_create_draft.assert_called_once()

                # Inspect the arguments passed to _create_draft
                args, kwargs = mock_create_draft.call_args
                title, content, thumb_media_id, author, digest = args
                
                assert title == "'测试文章'"
                assert author == "'测试作者'"
                assert thumb_media_id == 'mock_thumb_media_id'
                assert 'http://mock.url/image.png' in content

def test_get_access_token_failure(publisher):
    """Test failure to get access token."""
    with patch.object(publisher.session, 'get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {'errcode': 40001, 'errmsg': 'invalid credential'}
        mock_get.return_value = mock_response
        
        token = publisher._get_access_token()
        assert token is None
