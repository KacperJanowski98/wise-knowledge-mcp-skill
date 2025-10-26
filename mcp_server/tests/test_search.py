"""
Unit tests for search functionality.
"""

import pytest
from unittest.mock import patch, Mock

# Import functions to test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from search import (
    generate_query_embedding,
    search_knowledge_base,
    format_search_result,
    get_collection_info,
)


class TestGenerateQueryEmbedding:
    """Tests for generate_query_embedding function."""

    @patch('search.openai_client')
    def test_generates_embedding_for_query(self, mock_openai, mock_openai_response):
        """Test that embedding is generated correctly for a query."""
        mock_openai.embeddings.create.return_value = mock_openai_response

        query = "what is business strategy?"
        embedding = generate_query_embedding(query)

        # Verify OpenAI API was called correctly
        mock_openai.embeddings.create.assert_called_once()
        call_args = mock_openai.embeddings.create.call_args
        assert call_args[1]['input'] == query
        assert call_args[1]['model'] == 'text-embedding-3-small'
        assert call_args[1]['dimensions'] == 512

        # Verify embedding is returned
        assert embedding == [0.1] * 512


class TestSearchKnowledgeBase:
    """Tests for search_knowledge_base function."""

    @patch('search.qdrant_client')
    @patch('search.generate_query_embedding')
    def test_searches_with_default_parameters(self, mock_generate, mock_qdrant, mock_qdrant_search_results):
        """Test search with default limit and score threshold."""
        mock_generate.return_value = [0.1] * 512
        mock_qdrant.search.return_value = mock_qdrant_search_results

        results = search_knowledge_base("business strategy")

        # Verify embedding was generated
        mock_generate.assert_called_once_with("business strategy")

        # Verify Qdrant search was called with correct parameters
        mock_qdrant.search.assert_called_once()
        call_args = mock_qdrant.search.call_args
        assert call_args[1]['collection_name'] == 'podcasts_transcripts'
        assert call_args[1]['query_vector'] == [0.1] * 512
        assert call_args[1]['limit'] == 5  # default
        assert call_args[1]['score_threshold'] == 0.0  # default

        # Verify results are formatted correctly
        assert len(results) == 2
        assert results[0]['score'] == 0.95
        assert results[0]['episode_title'] == "Test Episode 1"

    @patch('search.qdrant_client')
    @patch('search.generate_query_embedding')
    def test_searches_with_custom_parameters(self, mock_generate, mock_qdrant, mock_qdrant_search_results):
        """Test search with custom limit and score threshold."""
        mock_generate.return_value = [0.1] * 512
        mock_qdrant.search.return_value = mock_qdrant_search_results

        results = search_knowledge_base(
            query="marketing tips",
            limit=10,
            score_threshold=0.8
        )

        # Verify Qdrant search was called with custom parameters
        call_args = mock_qdrant.search.call_args
        assert call_args[1]['limit'] == 10
        assert call_args[1]['score_threshold'] == 0.8

    @patch('search.qdrant_client')
    @patch('search.generate_query_embedding')
    def test_returns_empty_list_when_no_results(self, mock_generate, mock_qdrant):
        """Test that empty list is returned when no results found."""
        mock_generate.return_value = [0.1] * 512
        mock_qdrant.search.return_value = []

        results = search_knowledge_base("nonexistent query")

        assert results == []


class TestFormatSearchResult:
    """Tests for format_search_result function."""

    def test_formats_result_with_all_fields(self, mock_qdrant_search_results):
        """Test formatting a result with all fields present."""
        result = mock_qdrant_search_results[0]
        formatted = format_search_result(result)

        assert formatted['score'] == 0.95
        assert formatted['episode_id'] == "ep_001"
        assert formatted['episode_title'] == "Test Episode 1"
        assert formatted['section_heading'] == "Introduction"
        assert formatted['content'] == "This is test content about business strategy."
        assert formatted['key_points'] == ["Point 1", "Point 2"]
        assert formatted['tags'] == ["strategy", "business"]
        assert formatted['source_file'] == "test.json"

    def test_formats_result_with_missing_optional_fields(self):
        """Test formatting a result with missing optional fields."""
        result = Mock()
        result.score = 0.75
        result.payload = {
            "episode_id": "ep_003",
            "episode_title": "Episode 3",
            "section_heading": "Section",
            "content": "Content here",
        }

        formatted = format_search_result(result)

        assert formatted['score'] == 0.75
        assert formatted['key_points'] == []
        assert formatted['tags'] == []


class TestGetCollectionInfo:
    """Tests for get_collection_info function."""

    @patch('search.qdrant_client')
    def test_returns_collection_info(self, mock_qdrant, mock_collection_info):
        """Test that collection info is returned correctly."""
        mock_qdrant.get_collection.return_value = mock_collection_info

        info = get_collection_info()

        # Verify Qdrant client was called
        mock_qdrant.get_collection.assert_called_once_with('podcasts_transcripts')

        # Verify info is formatted correctly
        assert info['collection_name'] == 'podcasts_transcripts'
        assert info['points_count'] == 100
        assert info['vectors_count'] == 100
        assert info['status'] == 'green'

    @patch('search.qdrant_client')
    def test_handles_error_gracefully(self, mock_qdrant):
        """Test that errors are handled gracefully."""
        mock_qdrant.get_collection.side_effect = Exception("Connection error")

        info = get_collection_info()

        # Verify error info is returned
        assert info['collection_name'] == 'podcasts_transcripts'
        assert 'error' in info
        assert info['status'] == 'unavailable'
        assert "Connection error" in info['error']
