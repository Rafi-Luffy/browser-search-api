import json
from typing import Any, Dict
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from server.services.search_service import search_service
from server.services.scraper_service import scraper_service
from server.services.crawler_service import crawler_service

router = APIRouter(tags=["MCP"])

MCP_TOOLS = [
    {
        "name": "search",
        "description": "Perform web search across engines (DuckDuckGo, Wikipedia, Reddit, GitHub, SearXNG) and return titles, URLs, and snippets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query or keywords with optional site: operator"},
                "limit": {"type": "integer", "description": "Number of results to return (1-20)", "default": 5},
                "engines": {"type": "array", "items": {"type": "string"}, "description": "Search engines to query"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "scrape",
        "description": "Scrape a web page and convert its content into clean markdown, html, or extract structured data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target web page URL to scrape"},
                "formats": {"type": "array", "items": {"type": "string"}, "default": ["markdown"]},
                "onlyMainContent": {"type": "boolean", "default": True},
            },
            "required": ["url"],
        },
    },
    {
        "name": "map_links",
        "description": "Extract all navigable internal and external links from a website URL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target site URL to map"},
                "limit": {"type": "integer", "default": 100},
            },
            "required": ["url"],
        },
    },
]


@router.get("/mcp")
async def mcp_info():
    return {
        "name": "Universal Web Search & Browser API MCP Server",
        "version": "1.0.0",
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": False},
        },
        "tools": MCP_TOOLS,
    }


@router.post("/mcp")
async def mcp_jsonrpc(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None},
        )

    msg_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "universal-web-search-api",
                    "version": "1.0.0",
                },
            },
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": MCP_TOOLS,
            },
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "search":
                q = arguments.get("query", "")
                limit = arguments.get("limit", 5)
                engines = arguments.get("engines")
                res = await search_service.search(query=q, limit=limit, engines=engines)
                content_text = json.dumps(res, indent=2, ensure_ascii=False)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": content_text}],
                    },
                }

            elif tool_name == "scrape":
                url = arguments.get("url", "")
                formats = arguments.get("formats", ["markdown"])
                only_main = arguments.get("onlyMainContent", True)
                res = await scraper_service.scrape(url=url, formats=formats, only_main_content=only_main)
                content_text = res.get("data", {}).get("markdown") or json.dumps(res, indent=2)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": content_text}],
                    },
                }

            elif tool_name == "map_links":
                url = arguments.get("url", "")
                limit = arguments.get("limit", 100)
                links = await scraper_service.map_links(url=url, limit=limit)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(links, indent=2)}],
                    },
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "isError": True,
                "result": {
                    "content": [{"type": "text", "text": f"Error executing tool {tool_name}: {str(e)}"}],
                },
            }

    elif method == "notifications/initialized":
        return JSONResponse(status_code=204, content=None)

    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
