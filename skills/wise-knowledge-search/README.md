# Wise Knowledge Search Skill

A Claude Code skill for searching podcast transcripts using semantic search via MCP server.

## What This Skill Does

This skill enables Claude to:
- Search podcast transcripts using natural language queries
- Retrieve relevant sections with key points and metadata
- Check knowledge base status and statistics
- Provide intelligent responses based on podcast content

## Prerequisites

Before using this skill, ensure:

1. **Qdrant is running**:
   ```bash
   cd docker
   docker compose up -d
   ```

2. **Knowledge base is populated**:
   ```bash
   cd wise_knowledge
   uv run python main.py
   ```

3. **MCP server is configured** in Claude Code or Claude Desktop:

   Add to your Claude Code MCP configuration (e.g., `~/.config/claude-code/mcp.json`):
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

4. **Environment variables** are set in `mcp_server/.env`:
   ```bash
   cd mcp_server
   cp .env.example .env
   # Add your OPENAI_API_KEY
   ```

## Installation

### Option 1: Local Skill (Development)

Copy this skill to your local Claude Code skills directory:

```bash
# macOS
cp -r skills/wise-knowledge-search ~/Library/Application\ Support/Claude/skills/

# Linux
cp -r skills/wise-knowledge-search ~/.config/claude/skills/

# Windows
cp -r skills/wise-knowledge-search %APPDATA%\Claude\skills\
```

### Option 2: Project-Local Skill

Claude Code can also load skills from your project. Ensure this directory structure exists:
```
wise_knowledge/
  skills/
    wise-knowledge-search/
      SKILL.md
      README.md
```

## Usage Examples

Once the skill is installed and the MCP server is running, Claude will automatically use it when relevant.

For **detailed examples with expected responses**, see [EXAMPLES.md](EXAMPLES.md).

### Quick Examples

**Topic Search:**
```
You: "What did the podcasts say about marketing strategy?"
→ Claude searches, returns relevant sections with citations
```

**Collection Status:**
```
You: "How many podcast episodes are in the knowledge base?"
→ Claude checks collection statistics
```

**Deep Dive:**
```
You: "Find all discussions about pricing strategies and summarize them"
→ Claude searches, groups by episode, synthesizes findings
```

**Polish Queries:**
```
You: "Znajdź odcinki o finansach i inwestowaniu"
→ Claude searches and responds in Polish
```

## Skill Behavior

- **Automatic activation**: Claude loads this skill when you ask about podcast content
- **Natural language**: Use conversational queries - the semantic search handles understanding
- **Polish support**: Works seamlessly with Polish content
- **Transparent**: Shows relevance scores and sources
- **Intelligent**: Suggests follow-up queries based on tags and results

## Troubleshooting

### Skill not activating
- Verify skill is in correct directory
- Restart Claude Code
- Check that SKILL.md frontmatter is valid YAML

### No search results
- Ensure Qdrant is running: `docker compose ps`
- Verify knowledge base has data: Use `get_collection_status`
- Try lowering `score_threshold` (default: 0.7)

### MCP server errors
- Check MCP server logs
- Verify `OPENAI_API_KEY` in `mcp_server/.env`
- Ensure MCP server path is correct in configuration

## Configuration

The skill uses these MCP tools from the wise-knowledge server:

1. **search_podcasts** - Semantic search with configurable limit and threshold
2. **get_collection_status** - Collection statistics and health check

Parameters can be adjusted in search queries:
- `limit`: 1-20 results (default: 5)
- `score_threshold`: 0.0-1.0 similarity (default: 0.7)

## Technical Details

- **Embedding Model**: text-embedding-3-small (512d)
- **Vector Store**: Qdrant
- **Distance Metric**: Cosine similarity
- **Search Method**: Semantic vector search
- **Content**: Polish podcast transcripts

## Documentation

- **[README.md](README.md)** - This file (installation and overview)
- **[SKILL.md](SKILL.md)** - Complete skill instructions for Claude
- **[EXAMPLES.md](EXAMPLES.md)** - Detailed usage examples with responses
- **[FAQ.md](FAQ.md)** - Frequently asked questions and troubleshooting
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and planned features

## Development

To modify this skill:

1. Edit [SKILL.md](SKILL.md)
2. Update examples, guidelines, or tool descriptions
3. Reload skill in Claude Code (restart session)

The skill follows the [Agent Skills specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md).

## Getting Help

- **Questions?** See [FAQ.md](FAQ.md)
- **Issues?** Check the troubleshooting section in FAQ
- **Examples?** Browse [EXAMPLES.md](EXAMPLES.md)

## License

MIT - Same as parent project (wise_knowledge)
