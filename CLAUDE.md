# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`wise_knowledge` is a vector search system for podcast transcripts. It processes JSON transcript files, generates embeddings using OpenAI's text-embedding-3-small model, and stores them in Qdrant for semantic search capabilities.

## Repository Structure

The repository has a two-tier structure: project root contains Docker config and transcript data, while `wise_knowledge/` contains the Python package.

```
.
├── docker/
│   └── compose.yaml           # Qdrant database container configuration
├── transcripts/               # JSON transcript files (at root level, not in wise_knowledge/)
│   ├── strategia_biznesu.json
│   └── *.json                 # Multiple transcript files
├── mcp_server/                # MCP server for semantic search
│   ├── tests/                 # Unit tests for MCP server
│   │   ├── conftest.py        # Shared fixtures
│   │   └── test_search.py     # Search functionality tests
│   ├── pyproject.toml         # MCP server dependencies
│   ├── .env.example           # Environment variables template
│   ├── search.py              # Core search functionality
│   └── main.py                # MCP server implementation
└── wise_knowledge/            # Python package directory (cd here for dev work)
    ├── tests/                 # Unit tests with pytest
    │   ├── conftest.py        # Shared fixtures (mock data, temp dirs)
    │   └── test_ingest_transcripts.py
    ├── pyproject.toml         # Project dependencies (uv-based)
    ├── .env.example           # Environment variables template
    ├── explore_database.ipynb # Jupyter notebook for data exploration
    ├── ingest_transcripts.py  # Core ingestion logic (functions)
    └── main.py                # Entry point (calls run_ingestion())
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
- **Point IDs**: Auto-incrementing integers (original `episode_id_section_N` stored in payload as `original_id`)

## Code Architecture

### Ingestion Pipeline (`ingest_transcripts.py`)

The ingestion script is organized as pure functions that can be tested independently:

1. **`ensure_collection_exists()`** - Checks/creates Qdrant collection with correct vector config
2. **`load_transcripts()`** - Reads all JSON files from `../transcripts/`, returns list of point dicts with `id`, `text`, and `payload`
3. **`get_embeddings(texts)`** - Batch generates embeddings via OpenAI API
4. **`upload_to_qdrant(points)`** - Processes points in batches, generates embeddings, uploads to Qdrant
5. **`run_ingestion()`** - Orchestrates the full pipeline (called by `main.py`)

Each transcript section becomes one Qdrant point with:
- **Vector**: 512-dim embedding of `section.content`
- **Payload**: episode metadata + section metadata + full content for retrieval

### Testing Strategy

Tests use pytest with extensive fixtures in `conftest.py`:
- `mock_transcript_file` - Sample transcript JSON structure
- `sample_embedding` - 512-dim mock embedding vector
- `temp_transcripts_dir` - Temporary directory with test JSON files
- `reset_env_vars` - Auto-applied fixture that sets safe test environment variables

Tests mock both OpenAI API calls and Qdrant client operations to avoid external dependencies.

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

## Docker Management

The Qdrant database runs in Docker with persistent storage:

```bash
# Start Qdrant
cd docker
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop (keeps data)
docker compose down

# Stop and delete all data
docker compose down -v
```

Service details:
- **Container**: wise_knowledge_qdrant
- **Ports**: 6333 (HTTP API), 6334 (gRPC API)
- **Volume**: qdrant_storage (persists across restarts)
- **Dashboard**: http://localhost:6333/dashboard

## MCP Server (Semantic Search API)

The `mcp_server/` directory provides a Model Context Protocol server that exposes the knowledge base via semantic search.

### Setup MCP Server

```bash
cd mcp_server
uv sync
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
```

### Run MCP Server

**Standalone (development):**
```bash
cd mcp_server
uv run python main.py
```

**As MCP server (for Claude Desktop):**

Add to MCP client configuration (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "wise-knowledge": {
      "command": "uv",
      "args": [
        "--directory",
        "/full/path/to/wise_knowledge/mcp_server",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

### Available MCP Tools

1. **search_podcasts** - Semantic search over transcripts
   - Parameters: `query` (required), `limit` (1-20, default 5), `score_threshold` (0.0-1.0)
   - Returns: Episode title, section content, key points, tags, relevance scores

2. **get_collection_status** - Get knowledge base statistics
   - Returns: Collection name, points count, status

### MCP Server Architecture

- **search.py** - Core functions: `generate_query_embedding()`, `search_knowledge_base()`, `format_search_result()`
- **main.py** - MCP server: tool registration, request routing, response formatting
- **tests/** - Unit tests with mocked OpenAI/Qdrant clients

Search flow:
1. Query → generate embedding (OpenAI API, same model as ingestion)
2. Vector search in Qdrant (cosine similarity)
3. Format and return results with metadata

### Run MCP Server Tests

```bash
cd mcp_server
uv sync --extra dev
uv run pytest
uv run pytest --cov  # with coverage
```
