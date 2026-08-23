# Universal Web Search & Browser API

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7.svg)](https://browser-search-api-jpf1.onrender.com)

A high-performance, universal **Web Search and Browser API backend and Python SDK**. Built to execute unlimited web searches across the entire internet, scrape clean Markdown/HTML, map sites, run background crawls, parse PDFs, and expose an **MCP (Model Context Protocol)** server for AI coding agents.

**Live Deployed Endpoint** · `https://browser-search-api-jpf1.onrender.com`  
**GitHub Repository** · `https://github.com/Rafi-Luffy/browser-search-api`  
**MCP Server** · `https://browser-search-api-jpf1.onrender.com/mcp`  
**Interactive Swagger Docs** · `https://browser-search-api-jpf1.onrender.com/docs`

---

## Features

- **Universal Multi-Engine Search**: Search the entire internet using DuckDuckGo, SearXNG, Google, Bing, Wikipedia, Reddit, and GitHub. Supports `site:` domain filters, deduplication, and optional inline Markdown scraping.
- **High-Speed Web Scraping**: Clean Markdown conversion (stripping ads, scripts, and clutter), HTML extraction, outgoing links discovery, and structured JSON Schema extraction.
- **Batch Multi-URL Scraping**: Scrape dozens or hundreds of URLs concurrently with asynchronous workers (`POST /v1/batch/scrape`).
- **Sitemap & Link Mapping**: Discover all links and site tree hierarchy from any URL (`POST /v1/map`).
- **Asynchronous Web Crawler**: Job-based recursive crawling with max depth and page limits, status polling, and cancellation (`POST /v1/crawl`).
- **Change Tracking & Diffs**: Detect text, content, and price modifications between snapshots using Git-style unified diffs or JSON diffs (`POST /v1/change-tracking/diff`).
- **PDF Document Parsing**: Extract structured text and Markdown from uploaded PDF documents (`POST /v1/parse`).
- **Built-in MCP Server**: Native Model Context Protocol support (`/mcp`) for direct integration with Claude Code, Cursor, Codex, and Antigravity.
- **Deployed on Render**: Active and live container on Render free tier.

---

## API Reference (Unified Architecture)

| Endpoint | Method | Description |
| -------- | :----: | ----------- |
| `/health` | `GET` | Real-time health check & active background crawl metrics |
| `/v1/capabilities` | `GET` | Server limits, supported engines, and features |
| `/v1/search` | `POST` | Universal search with multi-engine ranking & `site:` filters |
| `/v1/scrape` | `POST` | Extract clean Markdown, HTML, links, or JSON Schema |
| `/v1/batch/scrape` | `POST` | Concurrently scrape multiple web pages in one request |
| `/v1/map` | `POST` | Discover site links and internal navigation hierarchy |
| `/v1/crawl` | `POST` | Start asynchronous recursive web crawl jobs |
| `/v1/crawl/active` | `GET` | List active background crawl jobs |
| `/v1/crawl/{id}` | `GET` / `DELETE` | Check progress or cancel a crawl job by ID |
| `/v1/change-tracking/diff` | `POST` | Git-style and JSON diffs between page snapshots |
| `/v1/parse` | `POST` | Multipart PDF upload and text/markdown extraction |
| `/mcp` | `GET` / `POST` | Model Context Protocol for AI Agent tools |

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/Rafi-Luffy/browser-search-api.git
cd browser-search-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` to point to the live Render deployment or your local instance:

```dotenv
# Point to live Render endpoint:
CRW_API_URL=https://browser-search-api-jpf1.onrender.com
```

---

## Python Client Usage

```python
from main import api

# Universal Web Search across the internet
results = api.post("/v1/search", {
    "query": "Quantum computing machine learning 2026",
    "limit": 5
})
for r in results["data"]["results"]:
    print(f"[{r['position']}] {r['title']} -> {r['url']}")

# Domain-restricted search
medium_results = api.post("/v1/search", {
    "query": "site:medium.com python performance optimization",
    "limit": 3
})

# Scrape clean Markdown
page = api.post("/v1/scrape", {
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "formats": ["markdown"]
})
print(page["data"]["markdown"][:500])
```

---

## Model Context Protocol (MCP) Integration

Connect your coding agents directly to your deployed endpoint:

### Claude Code

```bash
claude mcp add --transport http websearch https://browser-search-api-jpf1.onrender.com/mcp
```

### Cursor & Codex

Configure in `~/.codex/config.toml`:

```toml
[mcp_servers.websearch]
url = "https://browser-search-api-jpf1.onrender.com/mcp"
```

---

## Running Test Suites

```bash
# Run full smoke tests on the live deployed endpoint
python smoke_test.py

# Test search queries across internet topics
python test_search_endpoints.py

# Test domain-restricted searches
python test_medium_searches.py

# Test ambiguous query resolution
python test_vague_searches.py
```
