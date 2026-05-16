# Quizscendence Frontend

React + TypeScript + Vite frontend for the Quizscendence project.

## Prerequisites

- Node.js 20+
- Backend running via Docker (see root README)

## Set up

1. Start the backend (from the project root):

   ```bash
   make up
   ```
2. Install dependencies:

   ```bash
   npm install
   ```
3. Copy the env file:

   ```bash
   cp .env.example .env
   ```
4. Start the dev server:

   ```bash
   npm run dev --prefix client
   ```
5. Open `http://localhost:5173` in your browser

## How to run
1. Enter the root folder:

   ```bash
   cd ./quiz
   ```
2. Run backend

   ```bash
   make up
   ``` 
3. Run Vite

   ```bash
   npm run dev --prefix client
   ```
4. Open url http://localhost:5173/

## Notes

- `VITE_API_URL` should be left empty in `.env` when using the dev server — Vite proxies API calls to the Docker backend automatically
- The backend must be running at `https://localhost:8443` for the proxy to work
- API docs available at https://localhost:8443/api/docs/#/account/account_users_logout_create

## Scripts

| Command             | Description                      |
| ------------------- | -------------------------------- |
| `npm run dev`     | Start dev server with hot reload |
| `npm run build`   | Build for production             |
| `npm run preview` | Preview production build locally |
