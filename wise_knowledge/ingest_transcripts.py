"""
Ingest podcast transcripts into Qdrant vector database.

This script:
1. Reads all JSON files from the transcripts/ directory
2. For each section in each transcript, generates an embedding using OpenAI's text-embedding-3-small model
3. Uploads vectors and metadata to Qdrant collection
4. Automatically creates the collection if it doesn't exist
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
from dotenv import load_dotenv

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Load environment variables
load_dotenv()

# ---------- CONFIGURATION ----------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # Optional for local instance
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "podcasts_transcripts")
TRANSCRIPTS_DIR = Path(os.getenv("TRANSCRIPTS_DIR", "../transcripts"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "64"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBED_DIM = int(os.getenv("EMBED_DIM", "512"))
# -----------------------------------

# Validate configuration
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable is required. Please set it in .env file.")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def ensure_collection_exists() -> None:
    """Create Qdrant collection if it doesn't exist."""
    existing_collections = [c.name for c in qdrant_client.get_collections().collections]

    if COLLECTION_NAME not in existing_collections:
        print(f"Creating collection '{COLLECTION_NAME}' (dimension={EMBED_DIM}, distance=COSINE)")
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI API.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors (each vector is a list of floats)
    """
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        dimensions=EMBED_DIM
    )
    return [item.embedding for item in response.data]


def load_transcripts() -> List[Dict[str, Any]]:
    """
    Load all JSON transcript files and prepare them for embedding.

    Returns:
        List of dictionaries containing section data and metadata
    """
    all_points = []

    # Get all JSON files from transcripts directory
    json_files = sorted(TRANSCRIPTS_DIR.glob("*.json"))

    if not json_files:
        print(f"Warning: No JSON files found in {TRANSCRIPTS_DIR}")
        return all_points

    print(f"Found {len(json_files)} transcript files")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                doc = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error reading {json_file.name}: {e}")
            continue

        # Extract metadata
        episode_id = doc.get("episode_id") or json_file.stem
        title = doc.get("title", "")
        summary = doc.get("summary", "")
        tags = doc.get("tags", [])
        sections = doc.get("sections", [])

        # Process each section
        for idx, section in enumerate(sections, start=1):
            heading = section.get("heading", f"Section {idx}")
            content = section.get("content", "").strip()
            key_points = section.get("key_points", [])

            # Skip sections with no content
            if not content:
                continue

            # Prepare payload with metadata
            payload = {
                "episode_id": episode_id,
                "episode_title": title,
                "summary": summary,
                "tags": tags,
                "section_heading": heading,
                "key_points": key_points,
                "source_file": json_file.name,
                "chunk_index": idx,
                "content": content,  # Store content for retrieval
            }

            all_points.append({
                "id": f"{episode_id}_section_{idx}",
                "text": content,
                "payload": payload
            })

    return all_points


def upload_to_qdrant(points: List[Dict[str, Any]]) -> None:
    """
    Generate embeddings and upload points to Qdrant in batches.

    Args:
        points: List of point dictionaries with id, text, and payload
    """
    print(f"\nProcessing {len(points)} sections in batches of {BATCH_SIZE}")

    for i in tqdm(range(0, len(points), BATCH_SIZE), desc="Uploading to Qdrant"):
        batch = points[i:i + BATCH_SIZE]

        # Extract texts for embedding
        texts = [point["text"] for point in batch]

        # Generate embeddings
        try:
            embeddings = get_embeddings(texts)
        except Exception as e:
            print(f"\nError generating embeddings for batch {i//BATCH_SIZE + 1}: {e}")
            continue

        # Create Qdrant points
        qdrant_points = [
            PointStruct(
                id=point["id"],
                vector=embedding,
                payload=point["payload"]
            )
            for point, embedding in zip(batch, embeddings)
        ]

        # Upload to Qdrant
        try:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=qdrant_points
            )
        except Exception as e:
            print(f"\nError uploading batch {i//BATCH_SIZE + 1} to Qdrant: {e}")
            continue


def run_ingestion():
    """Main execution flow for transcript ingestion."""
    print("=" * 60)
    print("Podcast Transcripts Ingestion Pipeline")
    print("=" * 60)
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Embedding dimensions: {EMBED_DIM}")
    print(f"Qdrant URL: {QDRANT_URL}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Transcripts directory: {TRANSCRIPTS_DIR.resolve()}")
    print("=" * 60)

    # Step 1: Ensure collection exists
    ensure_collection_exists()

    # Step 2: Load and prepare transcripts
    print("\nLoading transcripts...")
    points = load_transcripts()

    if not points:
        print("No sections found to process. Exiting.")
        return

    print(f"Prepared {len(points)} sections for embedding")

    # Step 3: Generate embeddings and upload
    upload_to_qdrant(points)

    # Step 4: Verify upload
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)
    print("\n" + "=" * 60)
    print("Successfully completed!")
    print(f"Total points in collection: {collection_info.points_count}")
    print("=" * 60)
