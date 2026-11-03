# One Dockerfile for every Next.js portal: docker build --build-arg APP=social-web --build-arg PORT=3000 -f infra/docker/portal.Dockerfile .
# NOTE: `npm ci` needs a package-lock.json that includes the new workspaces. Run `npm install` once at the repo root first.
FROM node:22-alpine AS deps
WORKDIR /workspace
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
COPY apps/admin/package.json apps/admin/package.json
COPY apps/social-web/package.json apps/social-web/package.json
COPY apps/personal-web/package.json apps/personal-web/package.json
COPY apps/researcher-web/package.json apps/researcher-web/package.json
COPY packages packages
RUN npm ci

FROM node:22-alpine AS builder
ARG APP
WORKDIR /workspace
COPY --from=deps /workspace/node_modules ./node_modules
COPY . .
RUN npm run build --workspace @healthspan/${APP}

FROM node:22-alpine AS runner
ARG APP
ARG PORT=3000
ENV NODE_ENV=production APP=${APP}
WORKDIR /workspace
COPY --from=builder /workspace /workspace
EXPOSE ${PORT}
CMD npm run start --workspace @healthspan/${APP}
