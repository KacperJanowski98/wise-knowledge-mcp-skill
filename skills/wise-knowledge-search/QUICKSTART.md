# Quick Start Guide

Get the wise-knowledge-search skill up and running in 5 minutes.

## Prerequisites Checklist

- [ ] Qdrant database running
- [ ] Podcast transcripts ingested into knowledge base
- [ ] OpenAI API key available
- [ ] Claude Code installed

## Step 1: Start Qdrant (if not running)

```bash
cd docker
docker compose up -d
```

Verify at http://localhost:6333/dashboard

## Step 2: Populate Knowledge Base (if empty)

```bash
cd wise_knowledge
cp .env.example .env
# Add your OPENAI_API_KEY to .env
uv sync
uv run python main.py
```

This will ingest all transcripts from `transcripts/` directory.

## Step 3: Configure MCP Server

```bash
cd mcp_server
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

## Step 4: Configure Claude Code

Add MCP server to your Claude Code configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/claude-code/mcp.json`

```json
{
  "mcpServers": {
    "wise-knowledge": {
      "command": "uv",
      "args": [
        "--directory",
        "/FULL/PATH/TO/wise_knowledge/mcp_server",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

Replace `/FULL/PATH/TO/` with your actual project path!

## Step 5: Install Skill

### Automatic Installation (macOS/Linux)

```bash
cd skills/wise-knowledge-search
./install.sh
```

### Manual Installation

**macOS:**
```bash
cp -r skills/wise-knowledge-search ~/Library/Application\ Support/Claude/skills/
```

**Linux:**
```bash
cp -r skills/wise-knowledge-search ~/.config/claude/skills/
```

**Windows:**
```powershell
xcopy skills\wise-knowledge-search %APPDATA%\Claude\skills\wise-knowledge-search\ /E /I
```

## Step 6: Restart Claude Code

Close and reopen Claude Code to load the skill.

## Step 7: Test the Skill

Open a new Claude Code conversation and try:

```
How many podcasts are in the knowledge base?
```

If you see collection statistics, it's working! 🎉

Now try:

```
What do the podcasts say about [your topic]?
```

## Verification

### Test MCP Server Standalone

```bash
cd mcp_server
uv run python -c "from search import get_collection_info; print(get_collection_info())"
```

Should output collection stats.

### Check Qdrant Dashboard

Visit http://localhost:6333/dashboard and verify:
- Collection "podcasts_transcripts" exists
- Points count > 0

### Verify Skill Installation

**macOS:**
```bash
ls ~/Library/Application\ Support/Claude/skills/wise-knowledge-search/
```

**Linux:**
```bash
ls ~/.config/claude/skills/wise-knowledge-search/
```

Should show SKILL.md and other files.

## Troubleshooting

### "Collection not found" error

```bash
cd wise_knowledge
uv run python main.py
```

Re-run ingestion to create collection.

### "OpenAI API error"

Check that `.env` files in both `wise_knowledge/` and `mcp_server/` have valid `OPENAI_API_KEY`.

### "MCP server not responding"

1. Check MCP configuration path is absolute (not relative)
2. Verify `uv` is in your PATH: `which uv`
3. Test MCP server manually: `cd mcp_server && uv run python main.py`

### Skill not activating

1. Verify SKILL.md is in correct location
2. Check YAML frontmatter is valid (no tabs, proper indentation)
3. Restart Claude Code
4. Try explicitly: "Use the wise-knowledge-search skill to find..."

## Next Steps

- **Learn by example**: Read [EXAMPLES.md](EXAMPLES.md)
- **Explore features**: See [README.md](README.md)
- **Get help**: Check [FAQ.md](FAQ.md)
- **Customize**: Edit [SKILL.md](SKILL.md) to adjust behavior

## Common First Queries

Try these to get familiar with the skill:

```
Show me the collection status
```

```
What topics are covered in the podcasts?
```

```
Find episodes about [business/technology/marketing/etc]
```

```
Search for "AI automation" with a low threshold to see more results
```

```
What are the key points from episodes about strategy?
```

## Support

- Issues? See [FAQ.md](FAQ.md) troubleshooting section
- Questions? Check [README.md](README.md)
- Advanced usage? Browse [EXAMPLES.md](EXAMPLES.md)

---

**Estimated setup time:** 5-10 minutes (excluding transcript ingestion, which depends on data size)

**You're all set!** Start asking Claude about your podcast content. 🎙️🔍
