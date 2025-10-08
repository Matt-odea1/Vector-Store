"""
test_text_preprocessing_service.py
Unit tests for TextPreprocessingService.preprocess_to_markdown.
"""
import pytest
from unittest.mock import MagicMock
from src.main.service.TextPreprocessingService import TextPreprocessingService

@pytest.fixture
def service():
    svc = TextPreprocessingService()
    svc.llm = MagicMock()
    return svc

def test_preprocess_to_markdown_string(service):
    service.llm.chat.return_value = "# Heading\nContent"
    result = service.preprocess_to_markdown("Some text")
    assert result.startswith("# Heading")

def test_preprocess_to_markdown_generator(service):
    service.llm.chat.return_value = iter(["# Heading", "\nContent"])
    result = service.preprocess_to_markdown("Some text")
    assert result.startswith("# Heading")

def test_preprocess_to_markdown_error(service):
    service.llm.chat.return_value = 123
    with pytest.raises(TypeError):
        service.preprocess_to_markdown("Some text")

