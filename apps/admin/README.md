# Healthspan Network Admin App

The Admin App is a separate, lightweight Next.js application for operational workflows. It is intentionally a private console (`noindex`) rather than a public SEO surface.

## Run locally

```powershell
Push-Location apps\admin
npm install
$env:API_INTERNAL_URL = "http://127.0.0.1:8000"
npm run dev
Pop-Location
```

Open `http://localhost:3001`. The admin login accepts accounts created by the API operator bootstrap command:

```powershell
docker compose exec api python -m app.cli create-admin admin@example.org
```

## Run with Docker Compose

```text
http://localhost:3001
```

The server-side proxy talks to the API over the Compose network (`API_INTERNAL_URL=http://api:8000`). Browser requests use short paths on the Admin App's origin; access/refresh tokens stay in `HttpOnly`, `SameSite=Strict` cookies and are never exposed to client JavaScript.

## MVP screens

- Overview: current moderation queue, account snapshot, audit activity where permitted, and truthful service-integration status.
- Moderation queue: review reports, require a reason, and record dismiss/remove/restrict decisions.
- User management: email lookup, role assignment (admins only), and account suspension/reactivation with an audit reason.
- Audit log: recent privileged events for admins and read-only auditors.

The UI uses server-checked role access; hidden navigation is not an authorization boundary. The backend remains authoritative for every operation.

## UI components

The Admin App uses the same shadcn `base-nova` setup as the member web app. Its button, card, badge, input, and select primitives live locally under `components/ui/`, with the shared color-token approach configured in `app/globals.css`.
