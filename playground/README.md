# CRW Browser API Playground

A local Next.js playground for testing the Kerala Ayurveda Browser API from your browser.

## Run locally

```bash
cd playground
npm install
npm run dev
```

Open `http://localhost:3000`.

## Notes

- The playground calls `https://crw-production-d1ce.up.railway.app` directly from the browser.
- Paste your `CRW_API_KEY` in the top bar. The key is stored only in browser storage on your machine.
- `/health` can be tested without an API key. Other endpoints require bearer auth.
- Generated curl is shown before you send a request and remains available after the response.
