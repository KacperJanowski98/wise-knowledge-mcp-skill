"""
Unit tests for transcript ingestion functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from qdrant_client.models import Distance, VectorParams, PointStruct, CollectionInfo, CollectionsResponse

# Import functions to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest_transcripts import (
    ensure_collection_exists,
    get_embeddings,
    load_transcripts,
    upload_to_qdrant,
)


class TestEnsureCollectionExists:
    """Tests for ensure_collection_exists function."""

    @patch('ingest_transcripts.qdrant_client')
    def test_creates_collection_when_not_exists(self, mock_client):
        """Test that collection is created when it doesn't exist."""
        # Mock empty collections list
        mock_collections = Mock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections

        ensure_collection_exists()

        # Verify collection was created
        mock_client.create_collection.assert_called_once()
        call_args = mock_client.create_collection.call_args
        assert call_args[1]['collection_name'] == 'podcasts_transcripts'
        assert isinstance(call_args[1]['vectors_config'], VectorParams)

    @patch('ingest_transcripts.qdrant_client')
    def test_skips_creation_when_exists(self, mock_client):
        """Test that collection creation is skipped when it already exists."""
        # Mock existing collection
        mock_collection = Mock()
        mock_collection.name = 'podcasts_transcripts'
        mock_collections = Mock()
        mock_collections.collections = [mock_collection]
        mock_client.get_collections.return_value = mock_collections

        ensure_collection_exists()

        # Verify collection was NOT created
        mock_client.create_collection.assert_not_called()


class TestGetEmbeddings:
    """Tests for get_embeddings function."""

    @patch('ingest_transcripts.openai_client')
    def test_returns_embeddings_for_texts(self, mock_openai):
        """Test that embeddings are correctly extracted from API response."""
        # Mock OpenAI API response
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6]),
        ]
        mock_openai.embeddings.create.return_value = mock_response

        texts = ["test text 1", "test text 2"]
        embeddings = get_embeddings(texts)

        # Verify API was called correctly
        mock_openai.embeddings.create.assert_called_once()
        call_args = mock_openai.embeddings.create.call_args
        assert call_args[1]['input'] == texts
        assert call_args[1]['model'] == 'text-embedding-3-small'
        assert call_args[1]['dimensions'] == 512

        # Verify embeddings are correct
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]

    @patch('ingest_transcripts.openai_client')
    def test_handles_single_text(self, mock_openai):
        """Test that single text is handled correctly."""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai.embeddings.create.return_value = mock_response

        texts = ["single text"]
        embeddings = get_embeddings(texts)

        assert len(embeddings) == 1
        assert embeddings[0] == [0.1, 0.2, 0.3]


class TestLoadTranscripts:
    """Tests for load_transcripts function."""

    def test_loads_valid_transcript(self, tmp_path, mock_transcript_file):
        """Test loading a valid transcript JSON file."""
        # Create temporary transcripts directory with test file
        transcripts_dir = tmp_path / "transcripts"
        transcripts_dir.mkdir()

        test_file = transcripts_dir / "test_episode.json"
        test_file.write_text(json.dumps(mock_transcript_file))

        # Patch TRANSCRIPTS_DIR to use temp directory
        with patch('ingest_transcripts.TRANSCRIPTS_DIR', transcripts_dir):
            points = load_transcripts()

        # Verify points were created correctly
        assert len(points) == 2  # Two sections in mock data

        # Check first point
        assert points[0]['id'] == 'ep_test_section_1'
        assert points[0]['text'] == 'This is the content of the first section.'
        assert points[0]['payload']['episode_id'] == 'ep_test'
        assert points[0]['payload']['episode_title'] == 'Test Episode'
        assert points[0]['payload']['section_heading'] == 'Introduction'
        assert len(points[0]['payload']['key_points']) == 2

        # Check second point
        assert points[1]['id'] == 'ep_test_section_2'
        assert points[1]['payload']['section_heading'] == 'Main Topic'

    def test_skips_sections_without_content(self, tmp_path):
        """Test that sections with empty content are skipped."""
        transcripts_dir = tmp_path / "transcripts"
        transcripts_dir.mkdir()

        # Create transcript with empty section
        test_data = {
            "episode_id": "ep_test",
            "title": "Test",
            "sections": [
                {"heading": "Valid", "content": "Some content", "key_points": []},
                {"heading": "Empty", "content": "", "key_points": []},
                {"heading": "Whitespace", "content": "   ", "key_points": []},
            ]
        }
        test_file = transcripts_dir / "test.json"
        test_file.write_text(json.dumps(test_data))

        with patch('ingest_transcripts.TRANSCRIPTS_DIR', transcripts_dir):
            points = load_transcripts()

        # Only the section with actual content should be included
        assert len(points) == 1
        assert points[0]['payload']['section_heading'] == 'Valid'

    def test_handles_missing_optional_fields(self, tmp_path):
        """Test that missing optional fields are handled gracefully."""
        transcripts_dir = tmp_path / "transcripts"
        transcripts_dir.mkdir()

        # Minimal valid transcript
        test_data = {
            "sections": [
                {"content": "Content only"}
            ]
        }
        test_file = transcripts_dir / "minimal.json"
        test_file.write_text(json.dumps(test_data))

        with patch('ingest_transcripts.TRANSCRIPTS_DIR', transcripts_dir):
            points = load_transcripts()

        assert len(points) == 1
        assert points[0]['payload']['episode_id'] == 'minimal'
        assert points[0]['payload']['episode_title'] == ''
        assert points[0]['payload']['tags'] == []
        assert points[0]['payload']['section_heading'] == 'Section 1'

    def test_returns_empty_list_for_no_files(self, tmp_path):
        """Test that empty list is returned when no JSON files exist."""
        transcripts_dir = tmp_path / "transcripts"
        transcripts_dir.mkdir()

        with patch('ingest_transcripts.TRANSCRIPTS_DIR', transcripts_dir):
            points = load_transcripts()

        assert points == []

    def test_handles_invalid_json(self, tmp_path, capsys):
        """Test that invalid JSON files are handled gracefully."""
        transcripts_dir = tmp_path / "transcripts"
        transcripts_dir.mkdir()

        invalid_file = transcripts_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        with patch('ingest_transcripts.TRANSCRIPTS_DIR', transcripts_dir):
            points = load_transcripts()

        # Should return empty list and print error
        assert points == []
        captured = capsys.readouterr()
        assert "Error reading" in captured.out


class TestUploadToQdrant:
    """Tests for upload_to_qdrant function."""

    @patch('ingest_transcripts.qdrant_client')
    @patch('ingest_transcripts.get_embeddings')
    def test_uploads_points_in_batches(self, mock_get_embeddings, mock_client):
        """Test that points are uploaded in correct batches."""
        # Create test points
        points = [
            {
                'id': f'test_{i}',
                'text': f'content {i}',
                'payload': {'test': f'data_{i}'}
            }
            for i in range(5)
        ]

        # Mock embeddings
        mock_get_embeddings.return_value = [[0.1, 0.2] for _ in range(5)]

        # Test with batch size of 2
        with patch('ingest_transcripts.BATCH_SIZE', 2):
            upload_to_qdrant(points)

        # Should be called 3 times (batches of 2, 2, 1)
        assert mock_get_embeddings.call_count == 3
        assert mock_client.upsert.call_count == 3

    @patch('ingest_transcripts.qdrant_client')
    @patch('ingest_transcripts.get_embeddings')
    def test_creates_correct_point_structs(self, mock_get_embeddings, mock_client):
        """Test that PointStruct objects are created correctly."""
        points = [{
            'id': 'test_1',
            'text': 'test content',
            'payload': {'key': 'value'}
        }]

        mock_get_embeddings.return_value = [[0.1, 0.2, 0.3]]

        upload_to_qdrant(points)

        # Verify upsert was called with correct parameters
        mock_client.upsert.assert_called_once()
        call_args = mock_client.upsert.call_args

        assert call_args[1]['collection_name'] == 'podcasts_transcripts'
        uploaded_points = call_args[1]['points']
        assert len(uploaded_points) == 1
        assert isinstance(uploaded_points[0], PointStruct)

    @patch('ingest_transcripts.qdrant_client')
    @patch('ingest_transcripts.get_embeddings')
    def test_continues_on_embedding_error(self, mock_get_embeddings, mock_client, capsys):
        """Test that process continues when embedding generation fails."""
        points = [
            {'id': 'test_1', 'text': 'content 1', 'payload': {}},
            {'id': 'test_2', 'text': 'content 2', 'payload': {}},
        ]

        # First batch fails, second succeeds
        mock_get_embeddings.side_effect = [
            Exception("API Error"),
            [[0.1, 0.2]]
        ]

        with patch('ingest_transcripts.BATCH_SIZE', 1):
            upload_to_qdrant(points)

        # Should attempt both batches
        assert mock_get_embeddings.call_count == 2
        # Only one successful upsert
        assert mock_client.upsert.call_count == 1

        captured = capsys.readouterr()
        assert "Error generating embeddings" in captured.out

    @patch('ingest_transcripts.qdrant_client')
    @patch('ingest_transcripts.get_embeddings')
    def test_continues_on_upload_error(self, mock_get_embeddings, mock_client, capsys):
        """Test that process continues when Qdrant upload fails."""
        points = [
            {'id': 'test_1', 'text': 'content 1', 'payload': {}},
            {'id': 'test_2', 'text': 'content 2', 'payload': {}},
        ]

        mock_get_embeddings.return_value = [[0.1, 0.2]]

        # First upload fails, second succeeds
        mock_client.upsert.side_effect = [
            Exception("Upload Error"),
            None
        ]

        with patch('ingest_transcripts.BATCH_SIZE', 1):
            upload_to_qdrant(points)

        # Both uploads attempted
        assert mock_client.upsert.call_count == 2

        captured = capsys.readouterr()
        assert "Error uploading batch" in captured.out
