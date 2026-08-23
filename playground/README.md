# Web Search & Browser API Playground

An interactive Next.js web application to test and debug all Web Search and Browser API endpoints visually in real-time.

## Features

- Test Web Search across multiple engines (`/v1/search`)
- Test single page scraping (`/v1/scrape`) and batch scraping (`/v1/batch/scrape`)
- Test sitemap and URL mapping (`/v1/map`)
- Test asynchronous background crawling (`/v1/crawl`)
- Test unified Git diffs and JSON change tracking (`/v1/change-tracking/diff`)
- Test PDF document parsing (`/v1/parse`)
- Configurable base URL (defaults to `http://localhost:8000` or your deployed Railway URL)
- Built-in cURL code generator and JSON response inspector

## Running the Playground

```bash
cd playground
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.
