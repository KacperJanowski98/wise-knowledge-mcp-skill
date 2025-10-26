"""
MCP Server for Wise Knowledge - Podcast Transcripts Search.

Provides semantic search tool for querying podcast transcripts stored in Qdrant.
"""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from search import search_knowledge_base, get_collection_info


# Initialize MCP server
app = Server("wise-knowledge-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available MCP tools.
    """
    return [
        Tool(
            name="search_podcasts",
            description=(
                "Search podcast transcripts using semantic search. "
                "Returns relevant sections from podcast episodes based on the query. "
                "Each result includes the episode title, section heading, content, key points, and relevance score."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query - can be a question or topic to search for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "score_threshold": {
                        "type": "number",
                        "description": "Minimum similarity score from 0.0 to 1.0 (default: 0.0)",
                        "default": 0.0,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_collection_status",
            description=(
                "Get status and statistics about the podcast transcripts collection. "
                "Returns information about the number of indexed sections and collection health."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool execution.
    """
    if name == "search_podcasts":
        # Extract parameters
        query = arguments.get("query")
        limit = arguments.get("limit", 5)
        score_threshold = arguments.get("score_threshold", 0.0)

        # Validate query
        if not query or not isinstance(query, str):
            return [TextContent(
                type="text",
                text="Error: 'query' parameter is required and must be a string"
            )]

        # Perform search
        try:
            results = search_knowledge_base(
                query=query,
                limit=limit,
                score_threshold=score_threshold
            )

            # Return results as JSON for programmatic use
            return [TextContent(type="text", text=json.dumps(results, ensure_ascii=False))]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error performing search: {str(e)}"
            )]

    elif name == "get_collection_status":
        # Get collection info
        try:
            info = get_collection_info()
            response = json.dumps(info, indent=2)
            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting collection status: {str(e)}"
            )]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """
    Run the MCP server.
    """
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
