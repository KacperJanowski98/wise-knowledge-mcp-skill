# Changelog

All notable changes to the wise-knowledge-search skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2025-10-26

### Added
- Initial release of wise-knowledge-search skill
- Support for `search_podcasts` MCP tool with configurable parameters
- Support for `get_collection_status` MCP tool
- Automatic skill activation for podcast-related queries
- Polish language support with proper grammar handling
- Comprehensive documentation:
  - SKILL.md with complete skill instructions
  - README.md with installation and usage guide
  - EXAMPLES.md with detailed use cases
  - claude-code-mcp-config.example.json for MCP setup
- Installation script (install.sh) for macOS and Linux
- Search strategy guidelines and best practices
- Error handling instructions
- Response formatting guidelines
- Example workflows for common scenarios

### Features
- Natural language query processing
- Semantic search with cosine similarity
- Configurable result limits (1-20)
- Adjustable score thresholds (0.0-1.0)
- Episode and section metadata retrieval
- Key points extraction
- Tag-based result enrichment
- Transparent relevance scoring
- Multi-query workflow support
- Collection status monitoring

### Documentation
- Complete installation instructions for macOS and Linux
- MCP server configuration examples
- Troubleshooting guide
- 8+ detailed usage examples
- Best practices for search queries
- Technical context and specifications

## [Unreleased]

### Planned
- Support for filtering by episode_id
- Support for filtering by tags
- Date-based filtering if timestamps are added to data
- Multi-language query support (if non-Polish content added)
- Advanced search operators (AND, OR, NOT)
- Result caching for improved performance
- Integration with other MCP servers (if available)
