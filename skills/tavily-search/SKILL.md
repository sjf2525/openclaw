---
name: tavily-search
description: Use the Tavily Search API for web searches when the default Brave Search API is not configured or when Tavily is preferred. This skill provides instructions for making search requests, parsing results, and integrating Tavily search into workflows. Use when: (1) User requests a web search, (2) Default web_search tool is unavailable, (3) Tavily API key is configured and ready.
---

# Tavily Search

## Overview

This skill enables web search using the Tavily Search API as an alternative to the default Brave Search. Tavily provides real-time, high-quality search results with a simple API.

## Quick Start

When you need to perform a web search, follow these steps:

1. **Check configuration**: Ensure the Tavily API key is configured in `/home/codespace/.openclaw/openclaw.json` under `tools.tavily.apiKey`.
2. **Make the search request**: Use the `web_fetch` tool to send a POST request to the Tavily API endpoint.
3. **Parse results**: Extract titles, URLs, and snippets from the JSON response.

## API Reference

**Endpoint**: `https://api.tavily.com/search`
**Method**: POST
**Content-Type**: `application/json`

**Request body**:
```json
{
  "query": "search query here",
  "api_key": "your-api-key-here",
  "max_results": 5,
  "include_answer": false,
  "include_images": false,
  "include_raw_content": false
}
```

**Response format**:
```json
{
  "results": [
    {
      "title": "Page title",
      "url": "https://example.com",
      "content": "Snippet of page content",
      "score": 0.95
    }
  ],
  "answer": "...",
  "images": [],
  "query_time_ms": 120
}
```

## Step-by-Step Search Procedure

1. **Construct the request**:
   - Use the configured API key (read from config or environment).
   - Set `query` to the user's search query.
   - Set `max_results` as needed (default 5).

2. **Send the request**:
   - Use `web_fetch` with `url=https://api.tavily.com/search`, `method=POST`, and `body` as JSON.
   - Example:
   ```javascript
   // In tool call:
   web_fetch({
     url: "https://api.tavily.com/search",
     method: "POST",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({
       query: "OpenClaw AI",
       api_key: "tvly-...",
       max_results: 5
     })
   })
   ```
   - Note: The `web_fetch` tool currently only supports GET requests; use `exec` with `curl` as an alternative.

3. **Parse and present results**:
   - Extract each result's `title`, `url`, and `content`.
   - Format as a readable list with sources.
   - Include the `query_time_ms` for performance context.

## Alternative: Using curl via exec

If `web_fetch` doesn't support POST, use `exec` with `curl`:

```bash
curl -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{"query":"search term","api_key":"tvly-..."}'
```

## Example User Request

**User**: "Search for the latest OpenClaw documentation"

**Assistant action**:
1. Read API key from config.
2. Execute curl command with query "latest OpenClaw documentation".
3. Parse JSON response and present top 3 results with titles and URLs.

## Integration Notes

- The default `web_search` tool uses Brave Search API and requires its own API key.
- This skill should be used when Brave Search is not configured or when Tavily is preferred.
- For repeated searches, consider caching results to reduce API calls.

## Troubleshooting

- **401 Unauthorized**: Check API key in config.
- **No results**: Try broadening the query.
- **Timeout**: Ensure network connectivity.
