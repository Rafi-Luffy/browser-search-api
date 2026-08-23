# Universal Web Search & Browser API

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E.svg)](https://railway.app)

A high-performance, universal **Web Search and Browser API backend and Python SDK**. Built to execute unlimited web searches across the entire internet, scrape clean Markdown/HTML, map sites, run background crawls, parse PDFs, and expose an **MCP (Model Context Protocol)** server for AI coding agents.

---

## Features

- 🌐 **Universal Multi-Engine Search**: Search the entire internet using DuckDuckGo, SearXNG, Google, Bing, Wikipedia, Reddit, and GitHub. Supports `site:` domain filters, deduplication, and optional inline Markdown scraping.
- ⚡ **High-Speed Web Scraping**: Clean Markdown conversion (stripping ads, scripts, and clutter), HTML extraction, outgoing links discovery, and structured JSON Schema extraction.
- 📦 **Batch Multi-URL Scraping**: Scrape dozens or hundreds of URLs concurrently with asynchronous workers.
- 🗺️ **Sitemap & Link Mapping**: Discover all links and site tree hierarchy from any URL.
- 🕷️ **Asynchronous Web Crawler**: Job-based recursive crawling with max depth and page limits, status polling, and cancellation.
- 📊 **Change Tracking & Diffs**: Detect text, content, and price modifications between snapshots using Git-style unified diffs or JSON diffs.
- 📄 **PDF Document Parsing**: Extract structured text and Markdown from uploaded PDF documents (`POST /v2/parse`).
- 🤖 **Built-in MCP Server**: Native Model Context Protocol support (`/mcp`) for direct integration with **Claude Code**, **Cursor**, **Codex**, and **Antigravity**.
- 🚀 **Railway-Ready**: One-click deployment to Railway with preconfigured `Dockerfile`, `Procfile`, and `railway.toml`.

---

## API Surface

| Capability                       | v1 Endpoint | v2 Endpoint | Description |
| -------------------------------- | :---------: | :---------: | ----------- |
| Health & Status                  | `GET /health` | — | Real-time health check & active crawl metrics |
| Capabilities & Features          | `GET /v1/capabilities` | — | Server limits, supported engines & formats |
| Universal Web Search             | `POST /v1/search` | `POST /v2/search` | Search internet with multi-engine ranking & `site:` filters |
| Web Page Scraping                | `POST /v1/scrape` | `POST /v2/scrape` | Extract clean Markdown, HTML, links, or JSON Schema |
| Batch Multi-URL Scraping         | — | `POST /v2/batch/scrape` | Concurrently scrape multiple web pages |
| Site Link Mapping                | `POST /v1/map` | `POST /v2/map` | Discover site links and internal navigation |
| Recursive Background Crawling    | `POST /v1/crawl` | `POST /v2/crawl` | Start asynchronous recursive web crawl jobs |
| Crawl Status & Cancel            | `GET/DELETE /v1/crawl/{id}` | `GET /v2/crawl/active` | Monitor or cancel active crawls |
| Content & Price Change Diffs     | `POST /v1/change-tracking/diff` | — | Git-style diff between page snapshots |
| PDF Document Parsing             | — | `POST /v2/parse` | Multipart PDF upload and text/markdown extraction |
| MCP Protocol Endpoint            | `GET/POST /mcp` | `GET/POST /mcp` | Model Context Protocol for AI Agent tools |

---

## Quickstart (Local Development)

### 1. Clone and install dependencies

```bash
git clone https://github.com/raghavtapas-tech/browser-api-python.git
cd browser-api-python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Start the API Server

```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

Open interactive Swagger API documentation at: **`http://localhost:8000/docs`**

---

## Deploying to Railway for Unlimited Searches

This repository is preconfigured for zero-friction Railway deployment.

### Option A: Deploy via GitHub (Recommended)

1. Push your code to your GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "feat: universal web search API backend"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USER>/<YOUR_REPO>.git
   git push -u origin main
   ```
2. Log into [Railway.app](https://railway.app).
3. Click **"New Project"** -> **"Deploy from GitHub repo"** -> select your repository.
4. Railway will automatically detect the `Dockerfile` and `railway.toml` and deploy the service.
5. In your Railway Service Settings, click **"Generate Domain"** to get your public live URL (e.g. `https://your-app.up.railway.app`).

### Option B: Deploy via Railway CLI

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Environment Variables on Railway

Set these optional variables in your Railway service dashboard:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `PORT` | `8000` | Auto-injected by Railway |
| `CRW_API_KEY` | *(empty)* | Optional API token for Bearer authentication |
| `REQUIRE_AUTH` | `false` | Set to `true` to require authentication, or `false` for open unlimited searches |
| `SEARXNG_URL` | *(empty)* | Optional upstream SearXNG instance URL |
| `GITHUB_TOKEN` | *(empty)* | Optional GitHub Personal Access Token for GitHub search rate limits |

---

## Python Client Usage

The shared client in `main.py` connects seamlessly to either your local server or your deployed Railway endpoint:

```python
import os
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

## Model Context Protocol (MCP) Setup

Connect AI agents to your deployed API for unlimited live web search:

### Claude Code

```bash
claude mcp add --transport http websearch https://your-railway-url.up.railway.app/mcp
```

### Codex & Cursor

Configure in `~/.codex/config.toml`:

```toml
[mcp_servers.websearch]
url = "https://your-railway-url.up.railway.app/mcp"
```

---

## Test Suites

Run test suites locally or against your deployed Railway URL (configure `CRW_API_URL` in `.env`):

```bash
# Run full smoke test across all endpoints
python smoke_test.py

# Test search queries across topics
python test_search_endpoints.py

# Test domain-restricted searches
python test_medium_searches.py

# Test vague & ambiguous query resolution
python test_vague_searches.py

# Measure throughput & latency
python load_testing/load_test.py
```
