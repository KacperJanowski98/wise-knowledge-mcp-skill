"""
Semantic search functionality for podcast transcripts knowledge base.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "podcasts_transcripts")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBED_DIM = int(os.getenv("EMBED_DIM", "512"))
DEFAULT_SEARCH_LIMIT = int(os.getenv("DEFAULT_SEARCH_LIMIT", "5"))

# Validate configuration
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is required. Please set it in .env file.")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY if QDRANT_API_KEY else None,
    prefer_grpc=False  # Suppress insecure connection warning for local development
)


def generate_query_embedding(query: str) -> List[float]:
    """
    Generate embedding for a search query using OpenAI API.

    Args:
        query: Search query text

    Returns:
        Embedding vector as list of floats
    """
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
        dimensions=EMBED_DIM
    )
    return response.data[0].embedding


def search_knowledge_base(
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
    score_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Perform semantic search over podcast transcripts.

    Args:
        query: Search query text
        limit: Maximum number of results to return
        score_threshold: Minimum similarity score (0.0 to 1.0)

    Returns:
        List of search results with metadata and content
    """
    # Generate query embedding
    query_embedding = generate_query_embedding(query)

    # Search in Qdrant
    search_results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=limit,
        score_threshold=score_threshold
    )

    # Format results
    formatted_results = []
    for result in search_results:
        formatted_results.append(format_search_result(result))

    return formatted_results


def format_search_result(result: ScoredPoint) -> Dict[str, Any]:
    """
    Format a Qdrant search result into a readable dictionary.

    Args:
        result: ScoredPoint from Qdrant search

    Returns:
        Formatted result dictionary
    """
    payload = result.payload

    return {
        "score": round(result.score, 4),
        "episode_id": payload.get("episode_id"),
        "episode_title": payload.get("episode_title"),
        "section_heading": payload.get("section_heading"),
        "content": payload.get("content"),
        "key_points": payload.get("key_points", []),
        "tags": payload.get("tags", []),
        "source_file": payload.get("source_file"),
    }


def get_collection_info() -> Dict[str, Any]:
    """
    Get information about the Qdrant collection.

    Returns:
        Dictionary with collection statistics
    """
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        return {
            "collection_name": COLLECTION_NAME,
            "points_count": collection_info.points_count,
            "vectors_count": collection_info.vectors_count,
            "status": collection_info.status,
        }
    except Exception as e:
        return {
            "collection_name": COLLECTION_NAME,
            "error": str(e),
            "status": "unavailable"
        }
