"""
Pytest configuration and shared fixtures.
"""

import pytest
import json
from pathlib import Path


@pytest.fixture
def mock_transcript_file():
    """Fixture providing a sample transcript JSON structure."""
    return {
        "episode_id": "ep_test",
        "title": "Test Episode",
        "summary": "This is a test episode summary.",
        "tags": ["test", "example", "demo"],
        "sections": [
            {
                "heading": "Introduction",
                "content": "This is the content of the first section.",
                "key_points": [
                    "First key point",
                    "Second key point"
                ]
            },
            {
                "heading": "Main Topic",
                "content": "This is the main content discussing the topic in detail.",
                "key_points": [
                    "Main idea 1",
                    "Main idea 2",
                    "Main idea 3"
                ]
            }
        ]
    }


@pytest.fixture
def sample_embedding():
    """Fixture providing a sample 512-dimensional embedding vector."""
    # Return a simplified embedding (in reality it's 512-dim)
    return [0.1] * 512


@pytest.fixture
def mock_qdrant_collection_info():
    """Fixture providing mock Qdrant collection info."""
    from unittest.mock import Mock

    info = Mock()
    info.points_count = 10
    info.vectors_count = 10
    info.status = "green"
    return info


@pytest.fixture
def mock_openai_response(sample_embedding):
    """Fixture providing mock OpenAI API embedding response."""
    from unittest.mock import Mock

    response = Mock()
    item = Mock()
    item.embedding = sample_embedding
    response.data = [item]
    return response


@pytest.fixture
def sample_points():
    """Fixture providing sample points for upload."""
    return [
        {
            'id': 'ep_001_section_1',
            'text': 'Sample content for section 1',
            'payload': {
                'episode_id': 'ep_001',
                'episode_title': 'Test Episode',
                'section_heading': 'Introduction',
                'key_points': ['Point 1', 'Point 2'],
                'tags': ['test'],
                'source_file': 'test.json',
                'chunk_index': 1,
                'content': 'Sample content for section 1'
            }
        },
        {
            'id': 'ep_001_section_2',
            'text': 'Sample content for section 2',
            'payload': {
                'episode_id': 'ep_001',
                'episode_title': 'Test Episode',
                'section_heading': 'Main Content',
                'key_points': ['Point 3', 'Point 4'],
                'tags': ['test'],
                'source_file': 'test.json',
                'chunk_index': 2,
                'content': 'Sample content for section 2'
            }
        }
    ]


@pytest.fixture
def temp_transcripts_dir(tmp_path, mock_transcript_file):
    """
    Fixture creating a temporary transcripts directory with sample files.

    Returns the path to the temporary directory.
    """
    transcripts_dir = tmp_path / "transcripts"
    transcripts_dir.mkdir()

    # Create sample transcript file
    test_file = transcripts_dir / "sample_episode.json"
    test_file.write_text(json.dumps(mock_transcript_file))

    return transcripts_dir


@pytest.fixture(autouse=True)
def reset_env_vars(monkeypatch):
    """
    Automatically reset environment variables for each test.

    This ensures tests don't interfere with each other through env vars.
    """
    # Set safe test defaults
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION", "podcasts_transcripts")
    monkeypatch.setenv("EMBEDDING_MODEL", "text-embedding-3-small")
    monkeypatch.setenv("EMBED_DIM", "512")
    monkeypatch.setenv("BATCH_SIZE", "64")
