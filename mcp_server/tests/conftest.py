"""
Pytest configuration and shared fixtures for MCP server tests.
"""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_openai_response():
    """Fixture providing mock OpenAI API embedding response."""
    response = Mock()
    data_item = Mock()
    data_item.embedding = [0.1] * 512
    response.data = [data_item]
    return response


@pytest.fixture
def mock_qdrant_search_results():
    """Fixture providing mock Qdrant search results."""
    result1 = Mock()
    result1.id = 1
    result1.score = 0.95
    result1.payload = {
        "episode_id": "ep_001",
        "episode_title": "Test Episode 1",
        "section_heading": "Introduction",
        "content": "This is test content about business strategy.",
        "key_points": ["Point 1", "Point 2"],
        "tags": ["strategy", "business"],
        "source_file": "test.json",
    }

    result2 = Mock()
    result2.id = 2
    result2.score = 0.87
    result2.payload = {
        "episode_id": "ep_002",
        "episode_title": "Test Episode 2",
        "section_heading": "Main Topic",
        "content": "This is test content about marketing.",
        "key_points": ["Marketing tip 1", "Marketing tip 2"],
        "tags": ["marketing"],
        "source_file": "test2.json",
    }

    return [result1, result2]


@pytest.fixture
def mock_collection_info():
    """Fixture providing mock Qdrant collection info."""
    info = Mock()
    info.points_count = 100
    info.vectors_count = 100
    info.status = "green"
    return info


@pytest.fixture(autouse=True)
def reset_env_vars(monkeypatch):
    """
    Automatically reset environment variables for each test.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION", "podcasts_transcripts")
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-small")
    monkeypatch.setenv("EMBED_DIM", "512")
    monkeypatch.setenv("DEFAULT_SEARCH_LIMIT", "5")
