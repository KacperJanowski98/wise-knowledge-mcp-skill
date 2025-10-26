# Frequently Asked Questions (FAQ)

## General Questions

### Q: What is the wise-knowledge-search skill?
A: It's a Claude Code skill that enables semantic search over podcast transcripts stored in a Qdrant vector database. It allows Claude to intelligently search and retrieve relevant content from your podcast knowledge base.

### Q: Do I need to know how to code to use this skill?
A: No. Once installed and configured, you simply ask Claude questions in natural language, and the skill handles everything automatically.

### Q: Does this work with any podcasts?
A: The skill works with podcast transcripts that have been ingested into the wise_knowledge system. You need to first process your transcripts using the ingestion pipeline.

---

## Installation & Setup

### Q: Where do I install the skill?
A: You have two options:
- **Global**: Copy to `~/Library/Application Support/Claude/skills/` (macOS) or `~/.config/claude/skills/` (Linux)
- **Project-local**: Keep it in your project's `skills/` directory

### Q: What are the prerequisites?
A: You need:
1. Qdrant running (`docker compose up -d`)
2. Knowledge base populated (transcripts ingested)
3. MCP server configured in Claude Code
4. OpenAI API key set in `mcp_server/.env`

### Q: How do I configure the MCP server?
A: Add this to your Claude Code MCP configuration:
```json
{
  "mcpServers": {
    "wise-knowledge": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp_server", "run", "python", "main.py"]
    }
  }
}
```

See `claude-code-mcp-config.example.json` for a complete example.

### Q: The installation script fails on Windows. What do I do?
A: The install.sh script is for macOS/Linux. On Windows, manually copy the `wise-knowledge-search/` directory to:
```
%APPDATA%\Claude\skills\
```

---

## Usage

### Q: How do I activate the skill?
A: You don't! Claude automatically activates it when you ask questions about podcasts or the knowledge base. Just ask naturally:
- "What did the podcasts say about X?"
- "Find episodes discussing Y"
- "How many episodes are indexed?"

### Q: Can I search in Polish?
A: Yes! The skill fully supports Polish queries and will respond in Polish when appropriate. The semantic embeddings understand Polish language naturally.

### Q: What's the difference between threshold 0.5 and 0.9?
A:
- **0.9+**: Very strict, only near-exact semantic matches
- **0.7** (default): Balanced, good relevance
- **0.5-0.6**: Broader search, more exploratory
- Lower thresholds return more results but may be less relevant

### Q: How many results should I request?
A: Start with the default (5). Increase to 10-20 for:
- Comprehensive topic research
- Finding all mentions of something
- Exploratory searches

### Q: Can I search by episode title or tags?
A: Currently, the skill searches by semantic similarity to content. Tags and titles are returned in results and can help you filter mentally, but direct tag filtering isn't implemented yet (see CHANGELOG.md for planned features).

---

## Troubleshooting

### Q: Claude doesn't seem to be using the skill
**Possible causes:**
1. Skill not in correct directory → Check installation path
2. SKILL.md has syntax errors → Validate YAML frontmatter
3. MCP server not running → Test with `get_collection_status`
4. Skill not loaded → Restart Claude Code

### Q: I get "No results found" for everything
**Check these:**
1. Is the knowledge base populated? → Ask Claude to check collection status
2. Is Qdrant running? → `docker compose ps` in docker/ directory
3. Is your query too specific? → Try lowering threshold to 0.5
4. Does your content actually cover that topic? → Browse explore_database.ipynb

### Q: Search returns irrelevant results
**Solutions:**
1. **Raise threshold**: Try 0.8 or 0.9 for more precision
2. **Be more specific**: "customer acquisition strategies" instead of "customers"
3. **Check scores**: Results under 0.6 are usually weak matches
4. **Rephrase**: Try different wording or synonyms

### Q: MCP server errors or timeouts
**Debug steps:**
1. Check `mcp_server/.env` has `OPENAI_API_KEY`
2. Verify OpenAI API key is valid and has credits
3. Check Qdrant is accessible at localhost:6333
4. Look at MCP server logs (stdout/stderr)
5. Test MCP server standalone: `cd mcp_server && uv run python main.py`

### Q: Skill works but responses are slow
**Possible causes:**
- OpenAI API latency (embedding generation)
- Large number of results requested
- Slow internet connection
- Qdrant performance (unlikely with small datasets)

**Optimizations:**
- Reduce `limit` to 3-5 results
- Use higher `score_threshold` for faster filtering
- Check your internet speed

---

## Technical Questions

### Q: What embedding model is used?
A: OpenAI's `text-embedding-3-small` with 512 dimensions. Same model used during transcript ingestion.

### Q: How is similarity calculated?
A: Cosine similarity between query embedding and stored section embeddings. Scores range from 0.0 (completely different) to 1.0 (identical).

### Q: Can I use a different embedding model?
A: Technically yes, but you'd need to:
1. Re-ingest all transcripts with the new model
2. Update `mcp_server/.env` to use the new model
3. Ensure dimension compatibility

Not recommended unless you have specific requirements.

### Q: How much does it cost to use?
A: Costs depend on:
- **Ingestion**: One-time cost per transcript section (~$0.001 per 1000 sections)
- **Search**: ~$0.0001 per query (embedding generation)
- **Qdrant**: Free (self-hosted)

Typical usage costs are minimal (cents per month).

### Q: Is my data sent to OpenAI?
A: Only the text content for embedding generation. The embeddings and all metadata stay in your local Qdrant instance. See OpenAI's data usage policy for details.

### Q: Can I use this offline?
A: No, because:
- OpenAI API requires internet (for query embeddings)
- However, once embeddings are cached, you could theoretically use local embedding models

### Q: How do I update the skill?
A:
1. Pull latest changes from the repository
2. Re-run `./install.sh` or manually copy updated files
3. Restart Claude Code

---

## Content Questions

### Q: How do I add more podcasts?
A:
1. Add JSON transcripts to `transcripts/` directory
2. Run ingestion: `cd wise_knowledge && uv run python main.py`
3. New content is immediately searchable

### Q: Can I delete or update episodes?
A: Currently, the ingestion script adds new content. To update:
1. Stop Qdrant
2. Delete the collection or specific points
3. Re-run ingestion

See Qdrant docs for point management: https://qdrant.tech/documentation/

### Q: What's the maximum number of podcasts/episodes?
A: Limited by:
- Qdrant capacity (millions of vectors possible)
- Disk space for Qdrant storage
- OpenAI API rate limits during ingestion

Practical limit for hobby use: 1000+ episodes easily.

### Q: Can I use this for non-podcast content?
A: Absolutely! The system works with any text content structured as JSON with sections. Just follow the transcript JSON format.

---

## Performance & Limits

### Q: How fast are searches?
A: Typically:
- Embedding generation: 200-500ms (OpenAI API)
- Vector search: 10-50ms (Qdrant)
- Total: Usually under 1 second

### Q: What's the maximum query length?
A: OpenAI's embedding models support up to ~8000 tokens, but queries are typically 10-100 words for best results.

### Q: Can I search multiple queries in parallel?
A: Yes, Claude can execute multiple searches in one conversation turn if needed (e.g., "search for X and Y").

---

## Skill Development

### Q: Can I modify the skill?
A: Yes! The skill is open-source (MIT license). Edit `SKILL.md` to:
- Change activation triggers
- Adjust default parameters
- Modify response formatting
- Add new guidelines

### Q: How do I contribute improvements?
A:
1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

### Q: Where can I report bugs?
A: Open an issue in the wise_knowledge repository with:
- Skill version
- Claude Code version
- Error messages or unexpected behavior
- Steps to reproduce

---

## Getting Help

### Q: Where can I get more help?
A:
1. **Documentation**: Read [README.md](README.md) and [EXAMPLES.md](EXAMPLES.md)
2. **Project docs**: Check main project's [CLAUDE.md](../../CLAUDE.md)
3. **MCP docs**: https://modelcontextprotocol.io
4. **Qdrant docs**: https://qdrant.tech/documentation

### Q: Can I use this skill commercially?
A: Yes, under the MIT license. However:
- Check OpenAI's usage policies
- Ensure podcast content licensing allows it
- Consider privacy implications of your data

### Q: Is there a community or forum?
A: Check the main wise_knowledge project repository for:
- GitHub Discussions
- Issue tracker
- Contributing guidelines
