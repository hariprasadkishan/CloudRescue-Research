# CloudRescue — Research Dashboard Frontend

Interactive editorial research monograph and real-time visualization dashboard for the CloudRescue autonomic cloud resilience project.

Built with **React 19**, **Vite 8**, and **Tailwind CSS v4** following the *Variant A — Brutalist Swiss Monograph* aesthetic ([`DESIGN.md`](../CloudRescue_Project_Docs/DESIGN.md)).

---

## Architecture & Screen Layout

The dashboard presents the experimental evaluation across seven dedicated monograph screens:

1. **Screen 1 — Cover & Executive Brief:** Academic header, problem formulation, key findings scorecard, and research team attribution.
2. **Screen 2 — Research Inquiry:** Interactive ablation explorer (Baseline vs. Brownout-Only vs. Full CloudRescue) across 4 stress scenarios.
3. **Screen 3 — Simulation Environment:** Live/playback simulation inspector with per-worker queue depth, dimmer dynamics, and SLA violation charts.
4. **Screen 4 — Empirical Benchmark:** Grouped SLA failure rate ($V_{\text{overall}}$), latency inflation, and trade-off comparison cards.
5. **Screen 5 — Statistical Analytics:** Distributions of Jain's Fairness Index, CPU utilization, adaptation recovery times ($T_{\text{adapt}}$), and post-restoration nominal recovery ($T_{\text{restore}}$).
6. **Screen 6 — Methodology & Provenance:** Formal equations (velocity PI controller, BALB scoring), 5-stream PRNG architecture, and ADR logs.
7. **Screen 7 — Publication & Manuscript:** Certified signoff records, downloadable CSV/JSON artifact links, and IEEE bibliographic references.

---

## Getting Started

### Prerequisites
- **Node.js:** v18.0.0 or higher (tested on Node v22.22.2)
- **npm:** v9.0.0 or higher (tested on npm 10.9.7)
- **FastAPI Backend:** Ensure the backend is running at `http://127.0.0.1:8000` so the Vite dev server can proxy `/api` endpoints.

### Installation

```bash
cd frontend
npm install
```

### Running the Development Server

```bash
npm run dev
```

The application will start on `http://localhost:5173`.
Vite automatically proxies all `/api/*` HTTP requests to the FastAPI backend running at `http://127.0.0.1:8000`.

### Production Build

```bash
npm run build
```

Build outputs are compiled into `frontend/dist/`.

### Linting & Code Quality

```bash
npm run lint
```
Executes [Oxlint](https://oxc.rs/) across JSX/JS source modules.

---

## Backend Proxy Configuration

In `vite.config.js`:
```javascript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
  },
}
```
Ensure `uvicorn server.main:app --port 8000` is active before loading dynamic telemetry data.
