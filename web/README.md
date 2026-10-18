# Anchor dashboard

Local React + TypeScript + Vite operations console. It reads the Anchor API directly; it has no shadow network or fabricated fallback data.

## Run locally

Start Anchor's backend at `http://127.0.0.1:8765`, then from this directory:

```powershell
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to the loopback backend. For a production build, run `npm run build`; serve `dist/` behind a same-origin `/api` reverse proxy. The preview server also proxies `/api` to the same local backend.

All mutations are sent with `SIMULATION` mode or to the simulation-only API. The UI disables mutation controls unless `/api/health` reports `SIMULATION`.

The network endpoint returns bounded graph-derived entity records, relationships, locations, and summary counts. The dashboard renders those records on the tables and globe. No substitute topology is generated in the browser.

## Stack

- React 19.1.1, TypeScript 5.9.2, Vite 7.1.7
- `react-globe.gl` 2.38.0 (MIT), backed by `globe.gl` 2.46.2 (locked in `package-lock.json`)
- `lucide-react` 0.468.0
