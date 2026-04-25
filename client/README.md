# Quizscendence Frontend

React + TypeScript + Vite frontend for the Quizscendence project.

## Prerequisites

- Node.js 20+
- Backend running via Docker (see root README)

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy the env file:
   ```bash
   cp .env.example .env
   ```

3. Start the dev server:
   ```bash
   npm run dev
   ```

4. Open `http://localhost:5173` in your browser

## Notes

- `VITE_API_URL` should be left empty in `.env` when using the dev server — Vite proxies API calls to the Docker backend automatically
- The backend must be running at `https://localhost:8443` for the proxy to work
- API docs available at `https://localhost:8443/api/docs/`

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server with hot reload |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
