# API v1

## Identity
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/me`

## Social
- `GET /api/v1/feed`
- `POST /api/v1/posts`
- `GET /api/v1/posts/{id}`
- `POST /api/v1/posts/{id}/comments`
- `POST /api/v1/users/{id}/follow`
- `GET /api/v1/communities`
- `POST /api/v1/communities`

## Research
- `GET /api/v1/research/projects`
- `POST /api/v1/research/projects`
- `GET /api/v1/research/projects/{id}`
- `POST /api/v1/research/questions`
- `POST /api/v1/research/questions/{id}/hypotheses`
- `POST /api/v1/research/projects/{id}/literature`
- `POST /api/v1/research/projects/{id}/evidence`

## Search
- `GET /api/v1/search?q=...`
- `GET /api/v1/science/search?q=...`

## AI
- `POST /api/v1/ai/chat`
- `POST /api/v1/ai/research`
- `GET /api/v1/ai/runs/{id}`

The implementation should add authentication, authorization, pagination, idempotency, validation, rate limiting and structured error responses before production use.
