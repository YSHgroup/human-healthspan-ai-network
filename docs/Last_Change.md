# Overall progress implemented

The first frontend MVP shell is implemented. The public network introduction remains at `/`, and the app is available at `/home` with navigation for Home, Discover, Communities, Science, Research, and AI.

The API layer has typed post and research-question payloads, reads `NEXT_PUBLIC_API_URL` (defaulting to `http://localhost:8000`), and calls the live health, post-create, and research-question-create routes. Feed posts, the six MVP starter communities, and research projects are served through mock-backed data functions so screens do not import mock fixtures directly.

Home includes a post composer using a clearly temporary demo author ID. Research includes a research-question form. The app shell displays API health status. Discover, Science, and AI have initial placeholder pages.

The web app now includes the shadcn component setup and reusable UI components. Existing muted text styles use the dedicated `--muted-foreground` theme token, keeping copy readable across the public landing page and app shell while `--muted` remains the shadcn surface color.

----------
# Last Change

Resolved the text-color conflict between the existing styles and the shadcn theme by using `--muted-foreground` for muted copy. This preserves `--muted` as the shadcn background token and applies consistent readable text across the public landing page and app shell. Added the shadcn component setup and reusable Button, Card, Input, Tabs, and Avatar components.

----------
# What is the next step?

Implement backend authentication (`/auth/register`, `/auth/login`, and `/me`) and a real `GET /feed` endpoint. Then replace the mock feed with the API and remove the temporary hardcoded post author ID once authenticated identity is available.
