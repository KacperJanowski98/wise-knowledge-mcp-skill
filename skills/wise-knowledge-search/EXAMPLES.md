# Wise Knowledge Search Skill - Examples

This document provides practical examples of how Claude uses the wise-knowledge-search skill.

## Basic Search Examples

### Example 1: Topic Search

**User Query:**
```
What did the podcasts say about marketing strategy?
```

**How Claude Uses the Skill:**

1. Claude recognizes this as a knowledge base query
2. Activates the wise-knowledge-search skill
3. Uses the `search_podcasts` MCP tool:
   ```json
   {
     "query": "marketing strategy",
     "limit": 5,
     "score_threshold": 0.7
   }
   ```
4. Receives results with episode titles, sections, and key points
5. Formats response with citations and scores

**Expected Response:**
```
Found 3 relevant sections about marketing strategy:

1. Episode: "Strategia Biznesu #42" (Score: 0.89)
   Section: "Marketing w erze cyfrowej"

   Key Points:
   • Content marketing generates 3x more leads than traditional advertising
   • Social media engagement is crucial for brand building
   • Data-driven decisions improve campaign ROI by 40%

2. Episode: "Przedsiębiorca #15" (Score: 0.84)
   Section: "Budowanie marki"

   Key Points:
   • Consistency in messaging builds trust
   • Customer personas guide content creation
   • Multi-channel approach maximizes reach

Would you like me to explore any specific aspect of these strategies?
```

---

### Example 2: Collection Status

**User Query:**
```
How many podcast episodes are in the knowledge base?
```

**How Claude Uses the Skill:**

1. Recognizes this as a status query
2. Uses `get_collection_status` MCP tool (no parameters)
3. Retrieves collection statistics

**Expected Response:**
```
The knowledge base contains:
- Collection: podcasts_transcripts
- Total sections: 247 indexed chunks
- Status: Active and ready

These sections come from multiple podcast episodes, with each episode
divided into semantic sections for better search precision.
```

---

### Example 3: Exploratory Search

**User Query:**
```
Find anything related to AI and automation
```

**How Claude Uses the Skill:**

1. Performs initial search with default parameters
2. Analyzes tags from results
3. May suggest follow-up searches based on findings

**Expected Response:**
```
I found 5 sections discussing AI and automation:

Common themes across episodes:
- AI in business processes (3 mentions)
- Automation tools and platforms (2 mentions)
- Future of work with AI (2 mentions)

Top Results:

1. "Tech Trends 2024" - Section: "AI w biznesie" (Score: 0.91)
   This section discusses practical AI applications in small businesses...

2. "Automatyzacja 360" - Section: "Narzędzia do automatyzacji" (Score: 0.87)
   Covers tools like Zapier, Make.com, and custom scripts...

Tags found: #ai, #automatyzacja, #technologia, #przyszlosc-pracy

Would you like me to focus on a specific aspect like:
- AI tools and platforms?
- Impact on employment?
- Implementation strategies?
```

---

## Advanced Search Examples

### Example 4: Threshold Adjustment

**User Query:**
```
Search for anything about "pricing" but cast a wide net
```

**How Claude Uses the Skill:**

1. Recognizes need for broader search
2. Lowers `score_threshold` to 0.5 for more results
3. Increases `limit` to 10

```json
{
  "query": "pricing strategies pricing models",
  "limit": 10,
  "score_threshold": 0.5
}
```

**Expected Response:**
```
I've performed a broad search for pricing-related content. Found 8 sections
(showing scores for transparency):

High Relevance (0.8+):
1. "SaaS Startup Guide" - Pricing Models (0.87)
2. "Ecommerce Masterclass" - Dynamic Pricing (0.82)

Medium Relevance (0.6-0.8):
3. "Marketing Basics" - Value-Based Pricing (0.72)
4. "Product Strategy" - Competitive Pricing (0.68)
...

The broader search revealed discussions of:
- Subscription pricing models
- Value-based vs. cost-plus pricing
- Psychological pricing tactics
- Price optimization algorithms
```

---

### Example 5: Multi-Query Workflow

**User Query:**
```
Tell me about growth strategies, then find specific examples of customer acquisition
```

**How Claude Uses the Skill:**

1. First search: "growth strategies"
2. Analyzes results and tags
3. Second search: "customer acquisition" with context from first search
4. Synthesizes findings

**Search 1:**
```json
{
  "query": "growth strategies",
  "limit": 5,
  "score_threshold": 0.7
}
```

**Search 2:**
```json
{
  "query": "customer acquisition examples tactics",
  "limit": 7,
  "score_threshold": 0.65
}
```

**Expected Response:**
```
Let me break this down into two parts:

## Growth Strategies Overview

From 5 podcast sections, the main growth strategies discussed are:
- Product-led growth (3 mentions)
- Content marketing (2 mentions)
- Strategic partnerships (2 mentions)

## Customer Acquisition Examples

Following up with specific acquisition tactics, I found 7 detailed examples:

1. Episode: "Growth Hacking 101" (Score: 0.88)
   Example: Dropbox's referral program
   - Gave 500MB free storage per referral
   - Both referrer and referee benefited
   - Grew from 100k to 4M users in 15 months

2. Episode: "B2B Marketing Playbook" (Score: 0.84)
   Example: HubSpot's inbound methodology
   - Created valuable educational content
   - Free tools attracted leads
   - Nurtured with email sequences

[Additional examples...]

These examples align with the product-led and content marketing
strategies mentioned in the overview.
```

---

## Polish Language Examples

### Example 6: Native Polish Query

**User Query:**
```
Znajdź odcinki o finansach i inwestowaniu
```

**How Claude Uses the Skill:**

1. Processes Polish query directly (embeddings handle language)
2. Responds in Polish
3. Maintains proper diacritics and grammar

```json
{
  "query": "finanse inwestowanie",
  "limit": 5,
  "score_threshold": 0.7
}
```

**Expected Response:**
```
Znalazłem 4 odcinki poruszające tematy finansów i inwestowania:

1. "Finanse Osobiste #23" - Podstawy inwestowania (Score: 0.92)
   Sekcja: "Jak zacząć inwestować"

   Kluczowe punkty:
   • Zdefiniuj cele inwestycyjne przed rozpoczęciem
   • Diversyfikacja portfela minimalizuje ryzyko
   • Regularne inwestowanie (DCA) wygładza wahania rynku

2. "Biznes i Pieniądze" - Strategie inwestycyjne (Score: 0.86)
   Sekcja: "Długoterminowe vs. krótkoterminowe inwestycje"

   Kluczowe punkty:
   • Długoterminowe inwestycje korzystają z procentu składanego
   • Trading wymaga czasu i wiedzy
   • Pasywne indeksy często przewyższają aktywne fundusze

Czy chcesz, żebym zgłębił któryś z tych tematów?
```

---

## Error Handling Examples

### Example 7: No Results Found

**User Query:**
```
What do the podcasts say about quantum computing?
```

**How Claude Uses the Skill:**

1. Searches for "quantum computing"
2. Receives empty results
3. Suggests alternatives

**Expected Response:**
```
I didn't find any content about quantum computing in the knowledge base
(searched with threshold 0.7).

This could mean:
- The topic hasn't been covered in indexed podcasts
- It might be mentioned using different terminology

Would you like me to:
1. Try a broader search with lower threshold (0.5)?
2. Search for related topics like "advanced technology" or "computing"?
3. Check the collection status to see what topics are covered?
```

---

### Example 8: MCP Server Unavailable

**User Query:**
```
Search the podcasts for leadership advice
```

**If MCP Server is Not Running:**

**Expected Response:**
```
❌ I'm unable to connect to the knowledge base MCP server.

To resolve this:

1. Check if Qdrant is running:
   cd docker && docker compose ps

2. Start the MCP server:
   cd mcp_server && uv run python main.py

3. Verify MCP server configuration in Claude Code settings

4. Ensure OPENAI_API_KEY is set in mcp_server/.env

Once the server is running, I'll be able to search the podcast transcripts.
```

---

## Tips for Users

### Getting Better Results

1. **Use natural language**: "What did they say about X?" works better than just "X"
2. **Be specific**: "customer retention strategies" > "customers"
3. **Ask follow-ups**: Claude can refine searches based on initial results
4. **Request lower thresholds**: "cast a wide net" or "show me anything related"
5. **Combine with analysis**: "find X and summarize the common patterns"

### Understanding Scores

- **0.9+**: Highly relevant, exact topic match
- **0.8-0.9**: Very relevant, strong semantic similarity
- **0.7-0.8**: Relevant, good match (default threshold)
- **0.6-0.7**: Potentially relevant, broader match
- **Below 0.6**: Weak match, may not be directly related

### When to Check Collection Status

- Before starting: Verify data is loaded
- If searches fail: Confirm server connectivity
- For curiosity: See how much content is available
