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

## Architecture

The frontend follows an **MVVM-inspired pattern** where each page is self-contained in its own folder.

### File structure

```
src/
├── api/                        # All backend API calls — never fetch directly from components
├── components/                 # Shared reusable UI components used across pages
├── context/                    # Global state accessible from any component
└── pages/
    └── NamePage/
        ├── NamePage.tsx        # .tsx — layout only, composes sub-views, passes callbacks down
        ├── NamePage.css        # .css — page-level styles
        ├── useNamePage.ts      # .ts  — page hook: navigation, shared state, side effects
        └── SubviewsNamePage/
            └── FeatureView/
                ├── FeatureView.tsx      # .tsx — UI only, no business logic, receives props
                ├── FeatureView.css      # .css — view-level styles (optional)
                ├── useFeatureView.ts    # .ts  — business logic: API calls, state, validation
                └── SubviewsFeatureView/ # split further if the view grows too large
                    └── SmallPart/
                        ├── SmallPart.tsx
                        └── useSmallPart.ts
```

### Naming

- Page folders: `NamePage/`
- Sub-view folders: `SubviewsNamePage/`
- Components: `PascalCase` (`LoginView.tsx`)
- Hooks: `camelCase` starting with `use` (`useLoginView.ts`)

### Key rules

- Navigation is owned by the page hook and passed down as `onSuccess` callbacks — sub-views never call `navigate()` directly
- `.tsx` files contain UI only — no API calls, no `navigate()`
- `.ts` hook files contain all business logic — API calls, state, validation

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
