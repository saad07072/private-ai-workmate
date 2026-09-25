# Docker Deployment

This project deploys as a React static frontend served by nginx and a FastAPI backend. The frontend proxies `/api` and `/health` to the backend service, so the default production build does not expose a backend URL or any backend secret to the browser.

## Prerequisites

- Docker Engine 24 or newer with the Compose plugin.
- A Nebius Token Factory API key.
- A GitHub token only when private repositories or higher GitHub API limits are required.
- At least 4 GB of available memory for the backend, embeddings, and local Qdrant storage.

## Environment

Copy the templates without committing the resulting files:

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item .env.example .env
```

Set these values in `backend/.env`:

- `NEBIUS_API_KEY`: required for chat and embeddings.
- `NEBIUS_FAST_MODEL` and `NEBIUS_REASONING_MODEL`: existing Nemotron model settings.
- `GITHUB_TOKEN`: optional, for private repositories or higher API limits.
- `WORKMATE_TOOL_MODE=read_only`: keep the existing permission policy.

Set these values in the root `.env`:

- `VITE_API_BASE_URL`: normally empty for the nginx same-origin proxy. Set it only when the API is hosted at a separate public origin.
- `FRONTEND_PORT`: host port for nginx, default `80`.
- `CORS_ORIGINS`: comma-separated browser origins for direct backend access.
- `WORKMATE_COOKIE_SECURE=true` when the public site uses HTTPS.

Do not put credentials in `docker-compose.yml`, the frontend environment, or Vite source code.

## Build and Start

From the repository root:

```powershell
docker compose build
docker compose up -d
```

View service status and logs:

```powershell
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

## Health Verification

The backend health endpoint is available through nginx:

```powershell
curl http://localhost/health
```

Expected response:

```json
{"status":"healthy"}
```

Open `http://localhost` in a browser. The login page should load, and browser requests to `/api/auth/me` should return `401` until a user logs in or registers.

## Stop and Restart

Stop containers while preserving data:

```powershell
docker compose stop
```

Restart them:

```powershell
docker compose start
```

Rebuild after code changes:

```powershell
docker compose up -d --build
```

Remove containers without removing persistent volumes:

```powershell
docker compose down
```

Do not use `docker compose down -v` unless deleting all local application data is intentional.

## Persistent Data

Compose creates two named volumes:

- `workmate_data`: SQLite database, uploaded documents, and JSONL audit log.
- `qdrant_data`: embedded Qdrant collections and metadata.

The backend uses `/app/data/workmate.db`, `/app/data/documents`, `/app/data/tool_audit.jsonl`, and `/app/data/qdrant` inside the container. Never mount the same Qdrant directory into more than one backend process; embedded Qdrant is a single-process local store.

## Linux Cloud VM

1. Provision a Linux VM with Docker Engine and the Compose plugin.
2. Configure the VM firewall to expose only SSH and the public HTTP/HTTPS ports.
3. Install Git and clone the repository.
4. Copy the two environment templates as described above and add secrets directly on the VM.
5. Set `CORS_ORIGINS` to the real frontend origin and set `WORKMATE_COOKIE_SECURE=true` when TLS is enabled.
6. Put a TLS reverse proxy such as Caddy or an existing nginx instance in front of port `80`, or expose the stack through a secured load balancer.
7. Run `docker compose up -d --build`.
8. Verify `/health`, create the first account, and confirm chat, memory, document upload, GitHub read-only access, and security events.
9. Back up both named volumes. SQLite and embedded Qdrant should not be copied while actively writing unless using a consistent snapshot procedure.

For production operations, configure VM-level monitoring, log rotation, OS updates, TLS renewal, firewall rules, and secret rotation separately from this application stack.

## Vercel + Render

The repository includes `frontend/vercel.json` and `render.yaml` for a split deployment:

1. Create a Render Blueprint from the repository and apply `render.yaml`. Use a paid Render plan because the backend disk stores SQLite, uploaded documents, audit logs, and embedded Qdrant data. The disk must remain attached to exactly one backend instance.
2. In Render, set `NEBIUS_API_KEY`, optionally set `GITHUB_TOKEN`, and set `CORS_ORIGINS` to the final Vercel origin, for example `https://your-workmate.vercel.app`. Do not include a trailing slash or a path.
3. Deploy the `frontend` directory as a Vercel project. Set its Root Directory to `frontend`, Framework Preset to `Vite`, and add `VITE_API_BASE_URL` with the Render service URL, for example `https://private-ai-workmate-api.onrender.com`.
4. Redeploy both services after setting the final domains. Render uses `WORKMATE_COOKIE_SECURE=true` and `WORKMATE_COOKIE_SAMESITE=none` so the HttpOnly session cookie can be sent from the Vercel origin over HTTPS.
5. Verify the Render URL at `/health`, then register an account from the Vercel site and test chat, memory, document upload, and logout/login.

Render's free web services do not provide a persistent disk. Without persistent storage, the SQLite database, uploaded documents, audit log, and embedded Qdrant collections can disappear after a restart or redeploy. For multi-instance or higher-availability deployments, replace SQLite and embedded Qdrant with managed services before scaling the backend.

## Troubleshooting

### Frontend loads but API calls fail

Check `docker compose ps` and backend logs. The frontend uses the nginx service name `backend`, which only resolves inside the Compose network. Do not use `localhost` for the backend URL inside nginx.

### Backend is unhealthy

Inspect `docker compose logs backend`. Common causes are a missing `NEBIUS_API_KEY`, a malformed backend environment file, or a Qdrant volume permission problem.

### Qdrant reports that storage is locked

Run only one backend container against the embedded Qdrant volume. Stop duplicate local Uvicorn processes before starting a container that uses the same host-mounted data.

### Uploaded documents disappear

Confirm that the `workmate_data` volume exists and that the backend uses `/app/data/documents`. Do not use `docker compose down -v` during normal restarts.

### Cookies do not persist over HTTPS

Set `WORKMATE_COOKIE_SECURE=true`, serve the application over HTTPS, and ensure the reverse proxy forwards the original host and scheme headers.

### Port 80 is already in use

Set `FRONTEND_PORT=8080` in the root `.env`, then open `http://localhost:8080`.
