# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`wise_knowledge` is a vector search system for podcast transcripts. It processes JSON transcript files, generates embeddings using OpenAI's text-embedding-3-small model, and stores them in Qdrant for semantic search capabilities.

## Repository Structure

```
.
├── docker/
│   └── compose.yaml           # Qdrant database container configuration
├── transcripts/               # JSON transcript files (not in wise_knowledge/)
│   ├── strategia_biznesu.json
│   └── ...
└── wise_knowledge/            # Python package directory
    ├── pyproject.toml         # Project dependencies (uv-based)
    ├── .env.example           # Environment variables template
    ├── ingest_transcripts.py  # Main ingestion script
    └── main.py                # Entry point
```

## Transcript JSON Structure

Each transcript file contains:
- `episode_id`: Unique identifier for the episode
- `title`: Episode title
- `summary`: Overall episode summary
- `tags`: List of topic tags
- `sections[]`: Array of transcript sections, each with:
  - `heading`: Section title
  - `content`: Full text content (used for embedding)
  - `key_points`: List of key takeaways

## Development Setup

This project uses `uv` for dependency management.

### Install dependencies

```bash
cd wise_knowledge
uv sync
```

### Configure environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Start Qdrant database

```bash
cd docker
docker compose up -d
```

Qdrant will be available at:
- HTTP API: http://localhost:6333
- gRPC API: http://localhost:6334
- Dashboard: http://localhost:6333/dashboard

### Run transcript ingestion

```bash
cd wise_knowledge
uv run python main.py
```

This will:
1. Read all JSON files from `../transcripts/`
2. Generate 512-dim embeddings for each section's content
3. Upload to Qdrant collection `podcasts_transcripts`
4. Store metadata (episode_id, title, heading, key_points, tags, etc.)

### Run tests

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_ingest_transcripts.py

# Run tests with verbose output
uv run pytest -v
```

### Explore database (Jupyter)

```bash
# Install dev dependencies (includes Jupyter)
uv sync --extra dev

# Launch Jupyter Lab
uv run jupyter lab

# Or Jupyter Notebook
uv run jupyter notebook
```

Open `explore_database.ipynb` to view database statistics, visualizations, and sample data.

## Key Technical Details

- **Embedding Model**: text-embedding-3-small (512 dimensions)
- **Vector DB**: Qdrant (local instance via Docker)
- **Collection**: podcasts_transcripts (auto-created if missing)
- **Chunking Strategy**: One chunk = one transcript section
- **Distance Metric**: Cosine similarity
- **Batch Size**: 64 sections per API call

## Environment Variables

Required:
- `OPENAI_API_KEY`: OpenAI API key for embeddings

Optional (with defaults):
- `QDRANT_URL`: Qdrant server URL (default: http://localhost:6333)
- `QDRANT_COLLECTION`: Collection name (default: podcasts_transcripts)
- `EMBEDDING_MODEL`: OpenAI model (default: text-embedding-3-small)
- `EMBED_DIM`: Embedding dimensions (default: 512)
- `BATCH_SIZE`: Processing batch size (default: 64)
- `TRANSCRIPTS_DIR`: Path to transcripts folder (default: ../transcripts)

## Docker Services

- **qdrant**: Vector database with persistent storage volume
  - Ports: 6333 (HTTP), 6334 (gRPC)
  - Volume: qdrant_storage (data persists across restarts)
