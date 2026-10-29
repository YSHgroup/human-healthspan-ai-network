FROM node:22-alpine AS deps
WORKDIR /workspace
COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
COPY apps/admin/package.json apps/admin/package.json
COPY packages/ui/package.json packages/ui/package.json
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /workspace
COPY --from=deps /workspace/node_modules ./node_modules
COPY . .
RUN npm run build:web

FROM node:22-alpine AS runner
WORKDIR /workspace
ENV NODE_ENV=production
COPY --from=builder /workspace/package.json ./package.json
COPY --from=builder /workspace/package-lock.json ./package-lock.json
COPY --from=builder /workspace/apps/web ./apps/web
COPY --from=builder /workspace/apps/admin/package.json ./apps/admin/package.json
COPY --from=builder /workspace/packages/ui ./packages/ui
COPY --from=builder /workspace/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "run", "start", "--workspace", "@healthspan/web"]
