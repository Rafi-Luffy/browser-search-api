"use client";

import {
  Activity,
  Braces,
  Check,
  Clipboard,
  Eye,
  EyeOff,
  FileText,
  Globe,
  Loader2,
  Moon,
  Play,
  RefreshCw,
  Search,
  Shield,
  Sun,
  Trash2,
  Upload,
} from "lucide-react";
import { ReactNode, useEffect, useMemo, useState } from "react";

const DEFAULT_BASE_URL = "http://localhost:8000";

type Method = "GET" | "POST" | "DELETE";
type BodyKind = "none" | "json" | "multipart";
type EndpointId =
  | "health"
  | "capabilities"
  | "v1-scrape"
  | "v2-scrape"
  | "v1-search"
  | "v2-search"
  | "v1-map"
  | "v2-map"
  | "v1-crawl-start"
  | "v1-crawl-status"
  | "v1-crawl-cancel"
  | "v2-crawl-start"
  | "v2-crawl-active"
  | "v2-batch-scrape"
  | "v1-diff"
  | "v2-pdf-parse";
type PanelTab = "response" | "json" | "raw" | "curl";

type Endpoint = {
  id: EndpointId;
  group: string;
  label: string;
  method: Method;
  path: string;
  bodyKind: BodyKind;
  auth: boolean;
  description: string;
};

type PlaygroundState = {
  url: string;
  formats: string[];
  query: string;
  limit: number;
  mapUrl: string;
  crawlUrl: string;
  maxDepth: number;
  maxPages: number;
  crawlId: string;
  batchUrls: string;
  previousMarkdown: string;
  currentMarkdown: string;
  pdfFile: File | null;
  jsonSchema: string;
};

type ApiResult = {
  status: number;
  ok: boolean;
  elapsedMs: number;
  body: unknown;
  rawText: string;
};

type HistoryItem = {
  id: string;
  endpoint: string;
  status: number;
  elapsedMs: number;
  at: string;
};

const endpoints: Endpoint[] = [
  {
    id: "health",
    group: "System",
    label: "Health",
    method: "GET",
    path: "/health",
    bodyKind: "none",
    auth: false,
    description: "Public server health check.",
  },
  {
    id: "capabilities",
    group: "System",
    label: "Capabilities",
    method: "GET",
    path: "/v1/capabilities",
    bodyKind: "none",
    auth: true,
    description: "Inspect enabled API features and limits.",
  },
  {
    id: "v1-scrape",
    group: "Scrape",
    label: "Scrape Page",
    method: "POST",
    path: "/v1/scrape",
    bodyKind: "json",
    auth: true,
    description: "Scrape a page as Markdown, HTML, links, or structured JSON.",
  },
  {
    id: "v2-batch-scrape",
    group: "Batch",
    label: "Batch Scrape",
    method: "POST",
    path: "/v1/batch/scrape",
    bodyKind: "json",
    auth: true,
    description: "Scrape multiple URLs in one request.",
  },
  {
    id: "v1-search",
    group: "Search",
    label: "Web Search",
    method: "POST",
    path: "/v1/search",
    bodyKind: "json",
    auth: true,
    description: "Universal multi-engine web search endpoint.",
  },
  {
    id: "v1-map",
    group: "Map",
    label: "Site Map",
    method: "POST",
    path: "/v1/map",
    bodyKind: "json",
    auth: true,
    description: "Discover links from a site or page.",
  },
  {
    id: "v1-crawl-start",
    group: "Crawl",
    label: "Start Crawl",
    method: "POST",
    path: "/v1/crawl",
    bodyKind: "json",
    auth: true,
    description: "Start a background crawl job.",
  },
  {
    id: "v1-crawl-status",
    group: "Crawl",
    label: "Crawl Status",
    method: "GET",
    path: "/v1/crawl/{id}",
    bodyKind: "none",
    auth: true,
    description: "Check a crawl job by id.",
  },
  {
    id: "v2-crawl-active",
    group: "Crawl",
    label: "Active Crawls",
    method: "GET",
    path: "/v1/crawl/active",
    bodyKind: "none",
    auth: true,
    description: "List active crawl jobs.",
  },
  {
    id: "v1-crawl-cancel",
    group: "Crawl",
    label: "Cancel Crawl",
    method: "DELETE",
    path: "/v1/crawl/{id}",
    bodyKind: "none",
    auth: true,
    description: "Cancel a crawl job by id.",
  },
  {
    id: "v1-diff",
    group: "Diff",
    label: "Change Diff",
    method: "POST",
    path: "/v1/change-tracking/diff",
    bodyKind: "json",
    auth: true,
    description: "Compare previous and current Markdown content.",
  },
  {
    id: "v2-pdf-parse",
    group: "PDF",
    label: "Parse PDF",
    method: "POST",
    path: "/v1/parse",
    bodyKind: "multipart",
    auth: true,
    description: "Upload a PDF for text and markdown parsing.",
  },
];

const defaultState: PlaygroundState = {
  url: "https://en.wikipedia.org/wiki/Artificial_intelligence",
  formats: ["markdown"],
  query: "Quantum computing machine learning 2026",
  limit: 3,
  mapUrl: "https://en.wikipedia.org/wiki/Artificial_intelligence",
  crawlUrl: "https://en.wikipedia.org/wiki/Artificial_intelligence",
  maxDepth: 1,
  maxPages: 2,
  crawlId: "",
  batchUrls:
    "https://en.wikipedia.org/wiki/Artificial_intelligence\nhttps://en.wikipedia.org/wiki/Quantum_computing",
  previousMarkdown: "# Product Version\n- Version: 1.0.0\n- Price: $49",
  currentMarkdown: "# Product Version\n- Version: 1.1.0\n- Price: $39\n- Feature: AI Web Search",
  pdfFile: null,
  jsonSchema: JSON.stringify(
    {
      type: "object",
      properties: {
        title: { type: "string" },
        summary: { type: "string" },
      },
    },
    null,
    2,
  ),
};

const groupIcons: Record<string, ReactNode> = {
  System: <Activity size={16} />,
  Scrape: <FileText size={16} />,
  Search: <Search size={16} />,
  Map: <Globe size={16} />,
  Crawl: <RefreshCw size={16} />,
  Batch: <Braces size={16} />,
  Diff: <FileText size={16} />,
  PDF: <Upload size={16} />,
};

function groupEndpoints() {
  return endpoints.reduce<Record<string, Endpoint[]>>((acc, endpoint) => {
    acc[endpoint.group] = [...(acc[endpoint.group] ?? []), endpoint];
    return acc;
  }, {});
}

function buildPayload(endpoint: Endpoint, state: PlaygroundState) {
  switch (endpoint.id) {
    case "v1-scrape":
    case "v2-scrape": {
      const payload: Record<string, unknown> = {
        url: state.url,
        formats: state.formats,
      };
      if (state.formats.includes("json")) {
        payload.jsonSchema = safeParseJson(state.jsonSchema);
      }
      return payload;
    }
    case "v1-search":
    case "v2-search":
      return { query: state.query, limit: state.limit };
    case "v1-map":
    case "v2-map":
      return { url: state.mapUrl };
    case "v1-crawl-start":
      return {
        url: state.crawlUrl,
        maxDepth: state.maxDepth,
        maxPages: state.maxPages,
        formats: state.formats,
      };
    case "v2-crawl-start":
      return {
        url: state.crawlUrl,
        maxDepth: state.maxDepth,
        limit: state.maxPages,
      };
    case "v2-batch-scrape":
      return {
        urls: state.batchUrls
          .split(/\r?\n/)
          .map((url) => url.trim())
          .filter(Boolean),
        formats: state.formats,
      };
    case "v1-diff":
      return {
        previous: { markdown: state.previousMarkdown },
        current: { markdown: state.currentMarkdown },
        modes: ["gitDiff"],
      };
    default:
      return null;
  }
}

function safeParseJson(value: string) {
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function resolvePath(endpoint: Endpoint, state: PlaygroundState) {
  return endpoint.path.replace("{id}", encodeURIComponent(state.crawlId.trim()));
}

function generateCurl(
  endpoint: Endpoint,
  state: PlaygroundState,
  baseUrl: string,
  hasApiKey: boolean,
) {
  const path = resolvePath(endpoint, state);
  const lines = [`curl "${trimTrailingSlash(baseUrl)}${path}"`];
  if (endpoint.method !== "GET") {
    lines.push(`  -X ${endpoint.method}`);
  }
  if (endpoint.auth) {
    lines.push(
      hasApiKey
        ? `  -H "Authorization: Bearer $CRW_API_KEY"`
        : `  -H "Authorization: Bearer <CRW_API_KEY>"`,
    );
  }
  if (endpoint.bodyKind === "json") {
    lines.push(`  -H "Content-Type: application/json"`);
    lines.push(
      `  --data-raw '${JSON.stringify(buildPayload(endpoint, state))}'`,
    );
  }
  if (endpoint.bodyKind === "multipart") {
    lines.push(`  -F "file=@${state.pdfFile?.name ?? "path/to/file.pdf"}"`);
  }
  return lines.join(" \\\n");
}

function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, "");
}

function prettyJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function getNestedString(body: unknown, keys: string[]) {
  let cursor: unknown = body;
  for (const key of keys) {
    if (!cursor || typeof cursor !== "object" || !(key in cursor)) return null;
    cursor = (cursor as Record<string, unknown>)[key];
  }
  return typeof cursor === "string" ? cursor : null;
}

function getNestedArray(body: unknown, keys: string[]) {
  let cursor: unknown = body;
  for (const key of keys) {
    if (!cursor || typeof cursor !== "object" || !(key in cursor)) return null;
    cursor = (cursor as Record<string, unknown>)[key];
  }
  return Array.isArray(cursor) ? cursor : null;
}

export default function Home() {
  const [apiBaseUrl, setApiBaseUrl] = useState(DEFAULT_BASE_URL);
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [selectedId, setSelectedId] = useState<EndpointId>("v1-scrape");
  const [state, setState] = useState<PlaygroundState>(defaultState);
  const [result, setResult] = useState<ApiResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<PanelTab>("curl");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showAllHistory, setShowAllHistory] = useState(false);
  const [copyNotice, setCopyNotice] = useState("");

  const selectedEndpoint = endpoints.find((endpoint) => endpoint.id === selectedId)!;
  const grouped = useMemo(groupEndpoints, []);
  const curl = useMemo(
    () => generateCurl(selectedEndpoint, state, apiBaseUrl, Boolean(apiKey)),
    [apiBaseUrl, apiKey, selectedEndpoint, state],
  );
  const missingAuth = selectedEndpoint.auth && !apiKey.trim();
  const missingCrawlId =
    selectedEndpoint.path.includes("{id}") && !state.crawlId.trim();
  const missingPdf =
    selectedEndpoint.bodyKind === "multipart" && !state.pdfFile;
  const canSend = !loading && !missingAuth && !missingCrawlId && !missingPdf;
  const visibleHistory = showAllHistory ? history : history.slice(0, 6);

  useEffect(() => {
    const storedKey = window.localStorage.getItem("crw-playground-api-key");
    const storedBase = window.localStorage.getItem("crw-playground-base-url");
    const storedTheme = window.localStorage.getItem("crw-playground-theme");
    if (storedKey) setApiKey(storedKey);
    if (storedBase) setApiBaseUrl(storedBase);
    if (storedTheme === "light" || storedTheme === "dark") setTheme(storedTheme);
  }, []);

  useEffect(() => {
    window.localStorage.setItem("crw-playground-api-key", apiKey);
  }, [apiKey]);

  useEffect(() => {
    window.localStorage.setItem("crw-playground-base-url", apiBaseUrl);
  }, [apiBaseUrl]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    window.localStorage.setItem("crw-playground-theme", theme);
  }, [theme]);

  function updateState<K extends keyof PlaygroundState>(
    key: K,
    value: PlaygroundState[K],
  ) {
    setState((current) => ({ ...current, [key]: value }));
    setResult(null);
    setActiveTab("curl");
  }

  async function sendRequest() {
    if (!canSend) return;
    setLoading(true);
    setResult(null);
    const started = performance.now();
    const path = resolvePath(selectedEndpoint, state);
    const headers = new Headers();
    const requestInit: RequestInit = { method: selectedEndpoint.method, headers };

    if (selectedEndpoint.auth) {
      headers.set("Authorization", `Bearer ${apiKey.trim()}`);
    }

    if (selectedEndpoint.bodyKind === "json") {
      headers.set("Content-Type", "application/json");
      requestInit.body = JSON.stringify(buildPayload(selectedEndpoint, state));
    }

    if (selectedEndpoint.bodyKind === "multipart" && state.pdfFile) {
      const formData = new FormData();
      formData.append("file", state.pdfFile);
      requestInit.body = formData;
    }

    try {
      const response = await fetch(`${trimTrailingSlash(apiBaseUrl)}${path}`, requestInit);
      const rawText = await response.text();
      let body: unknown = rawText;
      try {
        body = rawText ? JSON.parse(rawText) : null;
      } catch {
        body = rawText;
      }
      const nextResult = {
        status: response.status,
        ok: response.ok,
        elapsedMs: Math.round(performance.now() - started),
        body,
        rawText,
      };
      setResult(nextResult);
      setActiveTab("response");
      setHistory((current) => [
        {
          id: crypto.randomUUID(),
          endpoint: selectedEndpoint.label,
          status: response.status,
          elapsedMs: nextResult.elapsedMs,
          at: new Date().toLocaleTimeString(),
        },
        ...current,
      ]);
    } catch (error) {
      setResult({
        status: 0,
        ok: false,
        elapsedMs: Math.round(performance.now() - started),
        body: {
          success: false,
          error:
            error instanceof Error
              ? error.message
              : "The browser could not complete the request.",
        },
        rawText: "",
      });
      setActiveTab("response");
    } finally {
      setLoading(false);
    }
  }

  async function copyText(label: string, value: string) {
    await navigator.clipboard.writeText(value);
    setCopyNotice(`${label} copied`);
    window.setTimeout(() => setCopyNotice(""), 1400);
  }

  return (
    <main className="min-h-screen bg-[#f7f8fb] text-slate-950 dark:bg-slate-950 dark:text-slate-100">
      <section className="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
        <div className="mx-auto flex max-w-[1500px] flex-col gap-3 px-4 py-4 lg:flex-row lg:items-center">
          <div className="flex h-10 min-w-[240px] items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 lg:mt-5 dark:border-slate-800 dark:bg-slate-900">
            <span className="grid size-6 place-items-center rounded bg-teal-50 text-teal-700 dark:bg-teal-950 dark:text-teal-300">
              <Braces size={14} />
            </span>
            <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              Browser API Playground
            </p>
          </div>
          <label className="flex flex-1 flex-col gap-1 text-xs font-medium text-slate-600 dark:text-slate-300">
            Base URL
            <input
              className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-950 outline-none focus:border-teal-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-teal-500"
              value={apiBaseUrl}
              onChange={(event) => setApiBaseUrl(event.target.value)}
            />
          </label>
          <label className="flex flex-1 flex-col gap-1 text-xs font-medium text-slate-600 dark:text-slate-300">
            API key
            <span className="flex h-10 items-center rounded-md border border-slate-300 bg-white focus-within:border-teal-600 dark:border-slate-700 dark:bg-slate-900 dark:focus-within:border-teal-500">
              <input
                className="h-full flex-1 bg-transparent px-3 text-sm text-slate-950 outline-none dark:text-slate-100"
                type={showKey ? "text" : "password"}
                placeholder="crw_live_..."
                value={apiKey}
                onChange={(event) => setApiKey(event.target.value)}
              />
              <button
                className="mr-1 grid size-8 place-items-center rounded text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                type="button"
                title={showKey ? "Hide API key" : "Show API key"}
                onClick={() => setShowKey((value) => !value)}
              >
                {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </span>
          </label>
          <button
            className="mt-5 grid size-10 place-items-center rounded-md border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 lg:mt-5 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            title="Clear settings"
            aria-label="Clear settings"
            onClick={() => {
              setApiBaseUrl(DEFAULT_BASE_URL);
              setApiKey("");
              setResult(null);
            }}
          >
            <Trash2 size={16} />
          </button>
          <button
            className="mt-5 grid size-10 place-items-center rounded-md border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 lg:mt-5 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
            type="button"
            title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            onClick={() => setTheme((value) => (value === "dark" ? "light" : "dark"))}
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </section>

      <section className="mx-auto grid max-w-[1500px] grid-cols-1 gap-4 px-4 py-4 lg:grid-cols-[260px_minmax(420px,1fr)_minmax(420px,0.95fr)]">
        <aside className="rounded-md border border-slate-200 bg-white p-3 lg:sticky lg:top-4 lg:max-h-[calc(100vh-120px)] dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-3 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
              Endpoints
            </p>
            <span className="rounded bg-teal-50 px-2 py-1 text-xs font-medium text-teal-700 dark:bg-teal-950 dark:text-teal-300">
              {endpoints.length} routes
            </span>
          </div>
          <nav className="space-y-4 lg:max-h-[calc(100vh-180px)] lg:overflow-y-auto lg:pr-1">
            {Object.entries(grouped).map(([group, items]) => (
              <div key={group}>
                <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                  {groupIcons[group]}
                  {group}
                </div>
                <div className="space-y-1">
                  {items.map((endpoint) => (
                    <button
                      key={endpoint.id}
                      className={`flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm transition ${
                        selectedId === endpoint.id
                          ? "bg-slate-950 text-white dark:bg-teal-500 dark:text-slate-950"
                          : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                      }`}
                      type="button"
                      onClick={() => {
                        setSelectedId(endpoint.id);
                        setResult(null);
                        setActiveTab("curl");
                      }}
                    >
                      <span>{endpoint.label}</span>
                      <span
                        className={`text-[11px] ${
                          selectedId === endpoint.id
                            ? "text-slate-300 dark:text-slate-800"
                            : "text-slate-400 dark:text-slate-500"
                        }`}
                      >
                        {endpoint.method}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </nav>
        </aside>

        <section className="rounded-md border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4 flex flex-col gap-2 border-b border-slate-200 pb-4 dark:border-slate-800">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded bg-slate-950 px-2 py-1 text-xs font-semibold text-white dark:bg-slate-100 dark:text-slate-950">
                {selectedEndpoint.method}
              </span>
              <code className="rounded bg-slate-100 px-2 py-1 text-sm text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                {selectedEndpoint.path}
              </code>
              {selectedEndpoint.auth ? (
                <span className="inline-flex items-center gap-1 rounded bg-amber-50 px-2 py-1 text-xs font-medium text-amber-700 dark:bg-amber-950 dark:text-amber-300">
                  <Shield size={13} />
                  bearer auth
                </span>
              ) : (
                <span className="rounded bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                  public
                </span>
              )}
            </div>
            <h1 className="text-xl font-semibold text-slate-950 dark:text-slate-100">
              {selectedEndpoint.label}
            </h1>
            <p className="text-sm text-slate-500 dark:text-slate-400">{selectedEndpoint.description}</p>
          </div>

          <EndpointForm
            endpoint={selectedEndpoint}
            state={state}
            updateState={updateState}
          />

          <div className="mt-5 flex flex-col gap-3 border-t border-slate-200 pt-4 sm:flex-row sm:items-center sm:justify-between dark:border-slate-800">
            <div className="space-y-1 text-sm">
              {missingAuth && (
                <p className="text-amber-700">Paste an API key to send this request.</p>
              )}
              {missingCrawlId && (
                <p className="text-amber-700">Enter a crawl id for this route.</p>
              )}
              {missingPdf && (
                <p className="text-amber-700">Choose a PDF file to upload.</p>
              )}
              {!missingAuth && !missingCrawlId && !missingPdf && (
                <p className="text-slate-500 dark:text-slate-400">
                  Curl is generated live from the controls.
                </p>
              )}
            </div>
            <button
              className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-teal-600 px-4 text-sm font-semibold text-white hover:bg-teal-700 disabled:cursor-not-allowed disabled:bg-slate-300 dark:bg-teal-500 dark:text-slate-950 dark:hover:bg-teal-400 dark:disabled:bg-slate-700 dark:disabled:text-slate-400"
              type="button"
              disabled={!canSend}
              onClick={sendRequest}
            >
              {loading ? <Loader2 className="animate-spin" size={16} /> : <Play size={16} />}
              Send request
            </button>
          </div>
        </section>

        <section className="rounded-md border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
          <div className="flex min-h-14 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
            <div>
              <p className="text-sm font-semibold text-slate-950 dark:text-slate-100">
                {result ? "Response" : "Generated curl"}
              </p>
              {result && (
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  HTTP {result.status || "network"} · {result.elapsedMs} ms
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {copyNotice && (
                <span className="inline-flex items-center gap-1 text-xs text-teal-700">
                  <Check size={14} />
                  {copyNotice}
                </span>
              )}
              <button
                className="grid size-8 place-items-center rounded text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                type="button"
                title="Copy curl"
                onClick={() => copyText("Curl", curl)}
              >
                <Clipboard size={16} />
              </button>
              {result && (
                <button
                  className="grid size-8 place-items-center rounded text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                  type="button"
                  title="Clear response"
                  onClick={() => {
                    setResult(null);
                    setActiveTab("curl");
                  }}
                >
                  <Trash2 size={16} />
                </button>
              )}
            </div>
          </div>

          <div className="flex border-b border-slate-200 px-3 dark:border-slate-800">
            {(["curl", "json", "response", "raw"] as PanelTab[]).map((tab) => (
              <button
                key={tab}
                className={`border-b-2 px-3 py-3 text-sm font-medium capitalize ${
                  activeTab === tab
                    ? "border-teal-600 text-teal-700 dark:border-teal-400 dark:text-teal-300"
                    : "border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
                }`}
                type="button"
                onClick={() => setActiveTab(tab)}
              >
                {tab === "json" ? "JSON" : tab}
              </button>
            ))}
          </div>

          <div className="min-h-[520px] p-4">
            {activeTab === "curl" && (
              <CodeBlock value={curl} copy={() => copyText("Curl", curl)} />
            )}
            {activeTab === "json" && (
              <CodeBlock
                value={result ? prettyJson(result.body) : prettyJson(buildPayload(selectedEndpoint, state))}
                copy={() =>
                  copyText(
                    result ? "JSON" : "Payload",
                    result ? prettyJson(result.body) : prettyJson(buildPayload(selectedEndpoint, state)),
                  )
                }
              />
            )}
            {activeTab === "raw" && (
              result ? (
                <CodeBlock
                  value={result.rawText || prettyJson(result.body)}
                  copy={() =>
                    copyText("Raw response", result.rawText || prettyJson(result.body))
                  }
                />
              ) : (
                <div className="flex h-[480px] items-center justify-center rounded-md border border-dashed border-slate-300 text-center dark:border-slate-700">
                  <div>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
                      No raw response yet
                    </p>
                    <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      Send a request to inspect the raw server response.
                    </p>
                  </div>
                </div>
              )
            )}
            {activeTab === "response" && (
              result ? (
                <ResponsePreview
                  endpoint={selectedEndpoint}
                  result={result}
                  copy={() => copyText("Response", prettyJson(result.body))}
                />
              ) : (
                <div className="flex h-[480px] items-center justify-center rounded-md border border-dashed border-slate-300 text-center dark:border-slate-700">
                  <div>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-200">
                      No response yet
                    </p>
                    <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                      Send a request to replace the curl preview with results.
                    </p>
                  </div>
                </div>
              )
            )}
          </div>

          {history.length > 0 && (
            <div className="border-t border-slate-200 px-4 py-3 dark:border-slate-800">
              <div className="mb-2 flex items-center justify-between gap-3">
                <p className="text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
                  Recent requests
                </p>
                {history.length > 6 && (
                  <button
                    className="rounded px-2 py-1 text-xs font-medium text-teal-700 hover:bg-teal-50 dark:text-teal-300 dark:hover:bg-teal-950"
                    type="button"
                    onClick={() => setShowAllHistory((value) => !value)}
                  >
                    {showAllHistory ? "Collapse" : `Show all ${history.length}`}
                  </button>
                )}
              </div>
              <div className="space-y-2">
                {visibleHistory.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400"
                  >
                    <span>{item.endpoint}</span>
                    <span>
                      {item.status} · {item.elapsedMs} ms · {item.at}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

function EndpointForm({
  endpoint,
  state,
  updateState,
}: {
  endpoint: Endpoint;
  state: PlaygroundState;
  updateState: <K extends keyof PlaygroundState>(
    key: K,
    value: PlaygroundState[K],
  ) => void;
}) {
  if (endpoint.id === "health" || endpoint.id === "capabilities" || endpoint.id === "v2-crawl-active") {
    return (
      <EmptyRequest
        text={
          endpoint.id === "health"
            ? "This public route sends no body."
            : "This authenticated GET route sends no body."
        }
      />
    );
  }

  if (endpoint.id.includes("scrape") && endpoint.id !== "v2-batch-scrape") {
    return (
      <div className="space-y-4">
        <TextField
          label="URL"
          value={state.url}
          onChange={(value) => updateState("url", value)}
        />
        <FormatPicker state={state} updateState={updateState} allowJson={endpoint.id === "v1-scrape"} />
        {state.formats.includes("json") && endpoint.id === "v1-scrape" && (
          <TextArea
            label="JSON schema"
            rows={8}
            value={state.jsonSchema}
            onChange={(value) => updateState("jsonSchema", value)}
          />
        )}
      </div>
    );
  }

  if (endpoint.id.includes("search")) {
    return (
      <div className="grid gap-4 sm:grid-cols-[1fr_120px]">
        <TextField
          label="Query"
          value={state.query}
          onChange={(value) => updateState("query", value)}
        />
        <NumberField
          label="Limit"
          value={state.limit}
          min={1}
          max={20}
          onChange={(value) => updateState("limit", value)}
        />
      </div>
    );
  }

  if (endpoint.id.includes("map")) {
    return (
      <TextField
        label="URL"
        value={state.mapUrl}
        onChange={(value) => updateState("mapUrl", value)}
      />
    );
  }

  if (endpoint.id === "v1-crawl-status" || endpoint.id === "v1-crawl-cancel") {
    return (
      <TextField
        label="Crawl ID"
        value={state.crawlId}
        onChange={(value) => updateState("crawlId", value)}
        placeholder="Paste id or jobId from a start crawl response"
      />
    );
  }

  if (endpoint.id === "v1-crawl-start" || endpoint.id === "v2-crawl-start") {
    return (
      <div className="space-y-4">
        <TextField
          label="URL"
          value={state.crawlUrl}
          onChange={(value) => updateState("crawlUrl", value)}
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <NumberField
            label="Max depth"
            value={state.maxDepth}
            min={0}
            max={5}
            onChange={(value) => updateState("maxDepth", value)}
          />
          <NumberField
            label={endpoint.id === "v1-crawl-start" ? "Max pages" : "Limit"}
            value={state.maxPages}
            min={1}
            max={100}
            onChange={(value) => updateState("maxPages", value)}
          />
        </div>
        {endpoint.id === "v1-crawl-start" && (
          <FormatPicker state={state} updateState={updateState} allowJson={false} />
        )}
      </div>
    );
  }

  if (endpoint.id === "v2-batch-scrape") {
    return (
      <div className="space-y-4">
        <TextArea
          label="URLs"
          rows={7}
          value={state.batchUrls}
          onChange={(value) => updateState("batchUrls", value)}
        />
        <FormatPicker state={state} updateState={updateState} allowJson={false} />
      </div>
    );
  }

  if (endpoint.id === "v1-diff") {
    return (
      <div className="grid gap-4 xl:grid-cols-2">
        <TextArea
          label="Previous Markdown"
          rows={12}
          value={state.previousMarkdown}
          onChange={(value) => updateState("previousMarkdown", value)}
        />
        <TextArea
          label="Current Markdown"
          rows={12}
          value={state.currentMarkdown}
          onChange={(value) => updateState("currentMarkdown", value)}
        />
      </div>
    );
  }

  if (endpoint.id === "v2-pdf-parse") {
    return (
      <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 text-center hover:border-teal-500 dark:border-slate-700 dark:bg-slate-950 dark:hover:border-teal-400">
        <Upload className="mb-3 text-slate-400 dark:text-slate-500" size={26} />
        <span className="text-sm font-medium text-slate-800 dark:text-slate-200">
          {state.pdfFile ? state.pdfFile.name : "Choose a PDF file"}
        </span>
        <span className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Sent as multipart form data to /v2/parse
        </span>
        <input
          className="hidden"
          type="file"
          accept="application/pdf,.pdf"
          onChange={(event) =>
            updateState("pdfFile", event.target.files?.[0] ?? null)
          }
        />
      </label>
    );
  }

  return <EmptyRequest text="No body fields for this request." />;
}

function FormatPicker({
  state,
  updateState,
  allowJson,
}: {
  state: PlaygroundState;
  updateState: <K extends keyof PlaygroundState>(
    key: K,
    value: PlaygroundState[K],
  ) => void;
  allowJson: boolean;
}) {
  const formats = allowJson
    ? ["markdown", "html", "links", "json"]
    : ["markdown", "html", "links"];
  return (
    <fieldset>
      <legend className="mb-2 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
        Formats
      </legend>
      <div className="flex flex-wrap gap-2">
        {formats.map((format) => {
          const checked = state.formats.includes(format);
          return (
            <label
              key={format}
              className={`inline-flex h-9 cursor-pointer items-center gap-2 rounded-md border px-3 text-sm ${
                checked
                  ? "border-teal-600 bg-teal-50 text-teal-800 dark:border-teal-400 dark:bg-teal-950 dark:text-teal-200"
                  : "border-slate-300 bg-white text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
              }`}
            >
              <input
                className="size-4 accent-teal-600"
                type="checkbox"
                checked={checked}
                onChange={(event) => {
                  const next = event.target.checked
                    ? [...state.formats, format]
                    : state.formats.filter((item) => item !== format);
                  updateState("formats", next.length ? next : ["markdown"]);
                }}
              />
              {format}
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}

function TextField({
  label,
  value,
  placeholder,
  onChange,
}: {
  label: string;
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
      {label}
      <input
        className="mt-2 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm normal-case text-slate-950 outline-none focus:border-teal-600 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-teal-500"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function NumberField({
  label,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="block text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
      {label}
      <input
        className="mt-2 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm normal-case text-slate-950 outline-none focus:border-teal-600 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-teal-500"
        type="number"
        min={min}
        max={max}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

function TextArea({
  label,
  value,
  rows,
  onChange,
}: {
  label: string;
  value: string;
  rows: number;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
      {label}
      <textarea
        className="mono mt-2 w-full resize-y rounded-md border border-slate-300 bg-white px-3 py-2 text-sm normal-case text-slate-950 outline-none focus:border-teal-600 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100 dark:focus:border-teal-500"
        rows={rows}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function EmptyRequest({ text }: { text: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
      {text}
    </div>
  );
}

function CodeBlock({ value, copy }: { value: string; copy: () => void }) {
  return (
    <div className="relative">
      <button
        className="absolute right-3 top-3 grid size-8 place-items-center rounded bg-white/90 text-slate-500 shadow-sm hover:bg-white dark:bg-slate-800/90 dark:text-slate-300 dark:hover:bg-slate-800"
        type="button"
        title="Copy"
        onClick={copy}
      >
        <Clipboard size={16} />
      </button>
      <pre className="mono max-h-[520px] overflow-auto rounded-md bg-slate-950 p-4 pr-14 text-sm leading-6 text-slate-100">
        {value}
      </pre>
    </div>
  );
}

function ResponsePreview({
  endpoint,
  result,
  copy,
}: {
  endpoint: Endpoint;
  result: ApiResult;
  copy: () => void;
}) {
  const markdown = getNestedString(result.body, ["data", "markdown"]);
  const links =
    getNestedArray(result.body, ["data", "links"]) ??
    getNestedArray(result.body, ["data", "urls"]) ??
    getNestedArray(result.body, ["data", "results"]);
  const diff =
    getNestedString(result.body, ["data", "gitDiff"]) ??
    getNestedString(result.body, ["data", "diff"]) ??
    getNestedString(result.body, ["gitDiff"]);
  const hasMarkdownPreview = Boolean(endpoint.id.includes("scrape") && markdown);
  const hasDiffPreview = Boolean(endpoint.group === "Diff" && diff);
  const hasItemsPreview = Boolean(links && links.length > 0);
  const hasSpecialPreview =
    hasMarkdownPreview || hasDiffPreview || hasItemsPreview;

  return (
    <div className="space-y-3">
      <div
        className={`flex items-center justify-between rounded-md border px-3 py-2 ${
          result.ok
            ? "border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300"
            : "border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300"
        }`}
      >
        <span className="text-sm font-semibold">
          {result.ok ? "Request completed" : "Request returned an error"}
        </span>
        <button
          className="inline-flex items-center gap-2 rounded px-2 py-1 text-xs font-medium hover:bg-white/70 dark:hover:bg-slate-800"
          type="button"
          onClick={copy}
        >
          <Clipboard size={14} />
          Copy
        </button>
      </div>

      {hasMarkdownPreview && (
        <PreviewCard title="Markdown preview">
          <pre className="mono max-h-[300px] overflow-auto whitespace-pre-wrap text-sm leading-6 text-slate-700 dark:text-slate-300">
            {markdown}
          </pre>
        </PreviewCard>
      )}

      {hasDiffPreview && (
        <PreviewCard title="Diff preview">
          <pre className="mono max-h-[300px] overflow-auto whitespace-pre-wrap text-sm leading-6 text-slate-700 dark:text-slate-300">
            {diff}
          </pre>
        </PreviewCard>
      )}

      {hasItemsPreview && links && (
        <PreviewCard title="Items">
          <div className="max-h-[300px] overflow-auto divide-y divide-slate-200">
            {links.slice(0, 30).map((item, index) => (
              <div key={`${index}-${JSON.stringify(item).slice(0, 30)}`} className="py-2 text-sm">
                {typeof item === "string" ? (
                  <a className="break-all text-teal-700 hover:underline" href={item} target="_blank">
                    {item}
                  </a>
                ) : (
                  <pre className="mono whitespace-pre-wrap text-xs text-slate-700 dark:text-slate-300">
                    {prettyJson(item)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </PreviewCard>
      )}

      {(!result.ok || !hasSpecialPreview) && (
        <PreviewCard title={result.ok ? "Response body" : "Error response"}>
          <pre className="mono max-h-[360px] overflow-auto whitespace-pre-wrap text-sm leading-6 text-slate-700 dark:text-slate-300">
            {prettyJson(result.body)}
          </pre>
        </PreviewCard>
      )}
    </div>
  );
}

function PreviewCard({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-md border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
      <div className="border-b border-slate-200 px-3 py-2 text-xs font-semibold uppercase text-slate-500 dark:border-slate-800 dark:text-slate-400">
        {title}
      </div>
      <div className="p-3">{children}</div>
    </div>
  );
}
