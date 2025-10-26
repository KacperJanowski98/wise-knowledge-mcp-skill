# Wise Knowledge MCP Server

MCP (Model Context Protocol) server providing semantic search over podcast transcripts stored in Qdrant vector database.

## Overview

This server exposes two MCP tools:
1. **search_podcasts** - Semantic search over podcast transcripts
2. **get_collection_status** - Get statistics about the knowledge base

## Setup

### 1. Install dependencies

```bash
cd mcp_server
uv sync
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key for generating query embeddings

Optional (with defaults):
- `QDRANT_URL` - Qdrant server URL (default: http://localhost:6333)
- `QDRANT_COLLECTION` - Collection name (default: podcasts_transcripts)
- `EMBEDDING_MODEL` - OpenAI model (default: text-embedding-3-small)
- `EMBED_DIM` - Embedding dimensions (default: 512)
- `DEFAULT_SEARCH_LIMIT` - Default number of results (default: 5)

### 3. Ensure Qdrant is running

```bash
cd ../docker
docker compose up -d
```

### 4. Ensure knowledge base is populated

```bash
cd ../wise_knowledge
uv run python main.py
```

## Running the Server

### Development (standalone)

```bash
cd mcp_server
uv run python main.py
```

### As MCP Server (for Claude Desktop, etc.)

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "wise-knowledge": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/wise_knowledge/mcp_server",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

For Claude Desktop on macOS, edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

For Claude Desktop on Windows, edit: `%APPDATA%\Claude\claude_desktop_config.json`

## Available Tools

### search_podcasts

Search podcast transcripts using semantic search.

**Parameters:**
- `query` (string, required) - Search query or question
- `limit` (integer, optional) - Max results to return (1-20, default: 5)
- `score_threshold` (number, optional) - Minimum similarity score 0.0-1.0 (default: 0.0)

**Example:**
```json
{
  "query": "jak zbudowa strategi biznesow?",
  "limit": 3,
  "score_threshold": 0.7
}
```

**Returns:**
- Episode title and section heading
- Full content of matching sections
- Key points from each section
- Relevance score (0.0-1.0)
- Tags

### get_collection_status

Get information about the knowledge base collection.

**Parameters:** None

**Returns:**
- Collection name
- Number of indexed sections (points_count)
- Collection status

## Testing

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_search.py

# Verbose output
uv run pytest -v
```

## Architecture

- **search.py** - Core search functionality (generate embeddings, query Qdrant, format results)
- **main.py** - MCP server implementation (tool registration, request handling)
- **tests/** - Unit tests with mocked OpenAI and Qdrant clients

## How It Works

1. User sends a search query via MCP tool
2. Server generates query embedding using OpenAI API (same model as ingestion)
3. Qdrant performs vector similarity search (cosine distance)
4. Results are formatted with metadata and returned to user
5. Each result includes relevance score, content, key points, and tags

## Dependencies

- `mcp>=1.0.0` - Model Context Protocol SDK
- `qdrant-client>=1.15.1` - Qdrant vector database client
- `openai>=1.58.1` - OpenAI API client for embeddings
- `python-dotenv>=1.0.0` - Environment variable management

## Troubleshooting

**Error: OPENAI_API_KEY not set**
- Create `.env` file with your OpenAI API key

**Error: Connection refused to Qdrant**
- Ensure Qdrant is running: `cd docker && docker compose up -d`
- Check Qdrant is accessible: http://localhost:6333/dashboard

**Error: Collection not found**
- Run ingestion first: `cd wise_knowledge && uv run python main.py`

**No results found**
- Ensure knowledge base is populated (check collection status tool)
- Try lowering `score_threshold` parameter
- Try broader search queries
