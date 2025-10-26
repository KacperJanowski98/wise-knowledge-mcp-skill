#!/usr/bin/env python3
"""
Simple MCP client for testing wise-knowledge server with Ollama.

This client allows you to query the podcast knowledge base using a local LLM (Ollama).
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

import ollama
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


class WiseKnowledgeClient:
    """Simple MCP client for querying podcast knowledge base."""

    def __init__(self):
        self.session: ClientSession | None = None
        self.available_tools: List[Any] = []
        self.exit_stack = None
        self.server_dir = os.getenv(
            "MCP_SERVER_DIR",
            str(Path(__file__).parent.parent / "mcp_server")
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect_to_server()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        return False

    async def connect_to_server(self):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command="uv",
            args=["--directory", self.server_dir, "run", "python", "main.py"],
            env=None
        )

        print(f"🔌 Connecting to MCP server at {self.server_dir}...")

        # Use async context manager properly
        self.exit_stack = stdio_client(server_params)
        stdio_transport = await self.exit_stack.__aenter__()
        read, write = stdio_transport

        self.session = ClientSession(read, write)
        await self.session.__aenter__()

        # Initialize session
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        self.available_tools = response.tools

        print(f"✅ Connected! Available tools: {[tool.name for tool in self.available_tools]}\n")

    async def search_knowledge_base(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search the podcast knowledge base."""
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_server() first.")

        result = await self.session.call_tool(
            "search_podcasts",
            arguments={
                "query": query,
                "limit": limit,
                "score_threshold": score_threshold
            }
        )

        # Parse the result
        if result.content:
            import json
            return json.loads(result.content[0].text)
        return []

    async def get_collection_status(self) -> Dict[str, Any]:
        """Get knowledge base collection status."""
        if not self.session:
            raise RuntimeError("Not connected to server. Call connect_to_server() first.")

        result = await self.session.call_tool("get_collection_status", arguments={})

        if result.content:
            import json
            return json.loads(result.content[0].text)
        return {}

    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for display."""
        if not results:
            return "❌ No results found."

        formatted = f"🔍 Found {len(results)} results:\n\n"

        for i, result in enumerate(results, 1):
            formatted += f"{'='*80}\n"
            formatted += f"Result {i} (Score: {result['score']})\n"
            formatted += f"{'='*80}\n"
            formatted += f"📺 Episode: {result['episode_title']}\n"
            formatted += f"📑 Section: {result['section_heading']}\n"
            formatted += f"🏷️  Tags: {', '.join(result['tags'])}\n\n"
            formatted += f"📝 Content:\n{result['content'][:500]}...\n\n"

            if result['key_points']:
                formatted += f"🔑 Key Points:\n"
                for point in result['key_points']:
                    formatted += f"  • {point}\n"
            formatted += "\n"

        return formatted

    async def chat_with_ollama(self, user_query: str, search_results: List[Dict[str, Any]]) -> str:
        """Use Ollama to generate a response based on search results."""

        # Build context from search results
        context = "Context from podcast transcripts:\n\n"
        for i, result in enumerate(search_results, 1):
            context += f"Source {i} (Score: {result['score']}):\n"
            context += f"Episode: {result['episode_title']}\n"
            context += f"Section: {result['section_heading']}\n"
            context += f"Content: {result['content']}\n"
            if result['key_points']:
                context += f"Key Points: {', '.join(result['key_points'])}\n"
            context += "\n"

        # Create prompt for Ollama
        prompt = f"""Based on the following context from podcast transcripts, answer the user's question.
If the context doesn't contain relevant information, say so.

{context}

User question: {user_query}

Answer (in Polish):"""

        print("\n🤖 Generating response with Ollama...\n")

        # Stream response from Ollama
        response = ""
        stream = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        for chunk in stream:
            content = chunk['message']['content']
            response += content
            print(content, end='', flush=True)

        print("\n")
        return response

    async def interactive_mode(self):
        """Run interactive chat mode."""
        print("\n" + "="*80)
        print("🎙️  Wise Knowledge - Interactive Chat")
        print("="*80)
        print("Ask questions about podcast content. Type 'exit' to quit.")
        print("Type 'status' to check collection status.")
        print("="*80 + "\n")

        while True:
            try:
                user_input = input("❓ Your question: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                if user_input.lower() == 'status':
                    status = await self.get_collection_status()
                    print(f"\n📊 Collection Status:")
                    print(f"  - Name: {status.get('collection_name')}")
                    print(f"  - Points: {status.get('points_count')}")
                    print(f"  - Status: {status.get('status')}\n")
                    continue

                # Search knowledge base
                print(f"\n🔍 Searching knowledge base...")
                results = await self.search_knowledge_base(user_input)

                if not results:
                    print("❌ No relevant results found. Try a different question.\n")
                    continue

                print(f"✅ Found {len(results)} relevant sections\n")

                # Generate response with Ollama
                await self.chat_with_ollama(user_input, results)

                # Ask if user wants to see detailed results
                show_details = input("\n📄 Show detailed search results? (y/n): ").strip().lower()
                if show_details == 'y':
                    print("\n" + self.format_search_results(results))

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.exit_stack:
            await self.exit_stack.__aexit__(None, None, None)


async def main():
    """Main entry point."""
    # Check if Ollama is available
    print("🔍 Checking Ollama availability...")
    try:
        ollama.list()
        print(f"✅ Ollama is running. Using model: {OLLAMA_MODEL}\n")
    except Exception:
        print("❌ Error: Ollama is not running or not accessible.")
        print("   Please start Ollama first: 'ollama serve'")
        print(f"   And pull the model: 'ollama pull {OLLAMA_MODEL}'")
        return

    # Use async context manager for proper cleanup
    async with WiseKnowledgeClient() as client:
        try:
            # Run interactive mode
            await client.interactive_mode()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
