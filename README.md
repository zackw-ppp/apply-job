# apply-job

A small, self-contained **job application tracker**. Log the roles you are
chasing, move each one through the pipeline (wishlist → applied → interviewing →
offer / rejected), and keep notes, links, and dates in one place.

It is a TypeScript monorepo with two workspaces:

| Workspace | Stack | Dev port |
| --- | --- | --- |
| `server` | Express + better-sqlite3 REST API | `4000` |
| `web` | React + Vite single-page app | `5173` |

The web dev server proxies `/api/*` to the API server, so the browser only ever
talks to `http://localhost:5173`.

## Requirements

- Node.js 20+ (a `.nvmrc` pins Node 22)
- A C/C++ toolchain for the native `better-sqlite3` build (`build-essential` on
  Debian/Ubuntu, which the Cloud Agent base image already provides)

## Getting started

```bash
npm install                 # installs both workspaces
npm --workspace server run seed   # optional: add a few sample applications
npm run dev                 # runs the API (4000) and the web app (5173)
```

Then open http://localhost:5173.

To run the services individually:

```bash
npm run dev:server   # API only, http://localhost:4000
npm run dev:web      # web only, http://localhost:5173
```

## Common commands

| Command | What it does |
| --- | --- |
| `npm run dev` | Run both dev servers together |
| `npm run build` | Type-check + build both workspaces |
| `npm run lint` | Lint both workspaces with ESLint |
| `npm run typecheck` | Type-check both workspaces |
| `npm test` | Run the API test suite (Vitest + Supertest) |
| `npm --workspace server run seed` | Seed the database with example data |

## Configuration

Copy `.env.example` to `.env` (or export the variables) to override defaults:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `4000` | API server port |
| `DATABASE_PATH` | `./data/apply-job.sqlite` | SQLite file location (`:memory:` for ephemeral) |
| `CORS_ORIGIN` | `http://localhost:5173` | Allowed browser origin for the API |

The SQLite database and `data/` directory are created automatically on first run
and are git-ignored.

## API

Base URL: `http://localhost:4000`

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Liveness check |
| `GET` | `/api/applications` | List applications (newest updated first) |
| `POST` | `/api/applications` | Create an application |
| `GET` | `/api/applications/:id` | Fetch one application |
| `PATCH` | `/api/applications/:id` | Update an application |
| `DELETE` | `/api/applications/:id` | Delete an application |

An application has `company` and `role` (required), a `status` (`wishlist`,
`applied`, `interviewing`, `offer`, `rejected`), and optional `location`, `url`,
`appliedOn` (`YYYY-MM-DD`), and `notes`.

## Cloud Agent environment

`.cursor/environment.json` configures the Cloud Agent dev environment: it runs
`npm install` plus the seed on setup, then launches the API and web dev servers
as two long-running terminals and exposes ports `4000` and `5173`.
