#!/bin/bash
# Installation script for wise-knowledge-search Claude Code skill

set -e

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    SKILLS_DIR="$HOME/Library/Application Support/Claude/skills"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    SKILLS_DIR="$HOME/.config/claude/skills"
else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "Please manually copy this directory to your Claude skills folder"
    exit 1
fi

SKILL_NAME="wise-knowledge-search"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Installing $SKILL_NAME skill to Claude Code..."
echo "📁 Skills directory: $SKILLS_DIR"

# Create skills directory if it doesn't exist
mkdir -p "$SKILLS_DIR"

# Copy skill to skills directory
if [ -d "$SKILLS_DIR/$SKILL_NAME" ]; then
    echo "⚠️  Skill already exists. Overwriting..."
    rm -rf "$SKILLS_DIR/$SKILL_NAME"
fi

cp -r "$SCRIPT_DIR" "$SKILLS_DIR/"

echo "✅ Skill installed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Ensure Qdrant is running: cd docker && docker compose up -d"
echo "2. Populate knowledge base: cd wise_knowledge && uv run python main.py"
echo "3. Configure MCP server in Claude Code (see README.md)"
echo "4. Set OPENAI_API_KEY in mcp_server/.env"
echo "5. Restart Claude Code to load the skill"
echo ""
echo "📖 For detailed instructions, see:"
echo "   $SCRIPT_DIR/README.md"
