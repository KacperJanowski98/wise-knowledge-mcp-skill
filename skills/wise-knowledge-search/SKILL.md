---
name: wise-knowledge-search
description: Search and query podcast transcripts knowledge base using semantic search via MCP server. Use this when the user asks about podcast content, wants to search transcripts, or needs information from the knowledge base.
---

# Wise Knowledge Search Skill

This skill enables semantic search over podcast transcripts stored in a Qdrant vector database through an MCP (Model Context Protocol) server.

## When to Use This Skill

Use this skill when:
- User asks questions about podcast content
- User wants to search for specific topics in transcripts
- User needs to find episodes discussing particular subjects
- User wants to retrieve key points or sections from podcasts
- User asks "what did the podcast say about X?"
- User requests collection statistics or status
- User will ask about business matters.
- User will ask about issues related to B2B sales and marketing.
- User will ask in a business context.

## Available MCP Tools

### 1. search_podcasts

Performs semantic search over podcast transcripts.

**Parameters:**
- `query` (required): Search query text in natural language
- `limit` (optional): Maximum number of results (1-20, default: 5)
- `score_threshold` (optional): Minimum similarity score 0.0-1.0 (default: 0.7)

**Returns:**
- Episode title and ID
- Section heading and content
- Key points from the section
- Tags associated with the episode
- Relevance score (cosine similarity)
- Source file name

**Example usage:**
```
When user asks: "Co mówiono o strategii marketingowej?"

Use search_podcasts with:
{
  "query": "strategia marketingowa",
  "limit": 5,
  "score_threshold": 0.7
}
```

### 2. get_collection_status

Retrieves statistics about the knowledge base collection.

**Parameters:** None

**Returns:**
- Collection name
- Number of points (transcript sections)
- Collection status
- Vector count

**Example usage:**
```
When user asks: "Ile odcinków jest w bazie?" or "Jaki jest status bazy wiedzy?"

Use get_collection_status
```

## Search Strategy Guidelines

1. **Query Formulation**: Use the user's natural language query directly - the embedding model handles semantic understanding
2. **Result Limit**: Start with 5 results, increase if user wants more comprehensive answers
3. **Score Threshold**:
   - Use 0.7 (default) for precise matches
   - Lower to 0.5-0.6 for broader, exploratory searches
   - Increase to 0.8+ for very specific queries
4. **Multiple Queries**: If first search yields no results, try rephrasing or lowering threshold

## Response Format

When presenting search results to the user:

1. **Summarize findings**: Start with a concise summary of what was found
2. **Cite sources**: Always mention episode title and section
3. **Include key points**: Present the key_points from results
4. **Show relevance**: Mention the similarity score for transparency
5. **Polish language**: Respond in Polish when content is in Polish

**Example response structure:**
```
Znalazłem 3 istotne fragmenty na temat strategii marketingowej:

1. **Odcinek: "Strategia Biznesu #42"** (Score: 0.89)
   - Sekcja: "Marketing w erze cyfrowej"
   - Kluczowe punkty:
     • [key point 1]
     • [key point 2]

2. **Odcinek: "..."** (Score: 0.85)
   ...

Czy chcesz, żebym rozwinął któryś z tych wątków?
```

## Technical Context

- **Embedding Model**: text-embedding-3-small (512 dimensions)
- **Vector Database**: Qdrant (local instance)
- **Collection**: podcasts_transcripts
- **Distance Metric**: Cosine similarity
- **Chunking Strategy**: One transcript section = one vector point

## Error Handling

If search returns no results:
1. Inform user that no matching content was found
2. Suggest trying broader keywords or lowering score_threshold
3. Offer to check collection status to verify data is loaded

If MCP server is unavailable:
1. Inform user the knowledge base server is not running
2. Suggest checking if Qdrant is running: `cd docker && docker compose ps`
3. Provide MCP server start command: `cd mcp_server && uv run python main.py`

## Integration Notes

- The MCP server must be running and configured in Claude Code
- Requires OpenAI API key for query embeddings (same model as ingestion)
- Qdrant must be running on localhost:6333 (default)
- All configuration in `mcp_server/.env`

## Example Workflows

### Workflow 1: Topic Research
```
User: "Co podcasty mówią o AI i automatyzacji?"

1. Use search_podcasts with query="AI automatyzacja"
2. Present top 5 results with key points
3. Offer to search for specific subtopics found
```

### Workflow 2: Episode Discovery
```
User: "Znajdź odcinki o finansach"

1. Use search_podcasts with query="finanse" and higher limit (10)
2. Group results by episode_id
3. Present unique episodes with their relevant sections
```

### Workflow 3: Deep Dive
```
User: "Powiedz mi więcej o tym, co mówili o strategii cenowej"

1. Use search_podcasts with query="strategia cenowa"
2. If results found, present detailed content
3. Offer related searches based on tags from results
```

## Best Practices

- **Always verify** MCP tools are available before using them
- **Use natural language** queries - don't over-engineer the search terms
- **Leverage metadata**: Use tags and episode titles to enrich responses
- **Be transparent**: Show scores so users understand relevance
- **Follow up**: Suggest related queries based on tags or key points found
- **Handle Polish content**: Maintain proper Polish grammar and diacritics
