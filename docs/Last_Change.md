# Overall progress implemented

The first frontend MVP shell is implemented. The public network introduction remains at `/`, and the app is available at `/home` with navigation for Home, Discover, Communities, Science, Research, and AI.

The API layer has typed post and research-question payloads, reads `NEXT_PUBLIC_API_URL` (defaulting to `http://localhost:8000`), and calls the live health, post-create, and research-question-create routes. Feed posts, the six MVP starter communities, and research projects are served through mock-backed data functions so screens do not import mock fixtures directly.

Home includes a post composer using a clearly temporary demo author ID. Research includes a research-question form. The app shell displays API health status. Discover, Science, and AI have initial placeholder pages.

The web app uses shadcn theme tokens and shared UI components across the public landing page and product routes. The theme is branded with the existing navy palette, has separate readable foreground/surface tokens, and uses Geist through a correctly mapped font variable.

----------
# Last Change

Migrated the landing page and product screens to shared shadcn Button, Card, Badge, Avatar, Input, Select, and Textarea components with Tailwind utilities. Rebuilt product navigation and API status styling on the shared theme. Fixed the muted text/surface token conflict and aligned shadcn colors and Geist typography with the Healthspan Network brand.

----------
# What is the next step?

Implement backend authentication (`/auth/register`, `/auth/login`, and `/me`) and a real `GET /feed` endpoint. Then replace the mock feed with the API and remove the temporary hardcoded post author ID once authenticated identity is available.
