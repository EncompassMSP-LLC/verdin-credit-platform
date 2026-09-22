FROM node:26-alpine AS base
RUN corepack enable && corepack prepare pnpm@9.15.0 --activate
WORKDIR /app

FROM base AS deps
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml* ./
COPY apps/web/package.json ./apps/web/
COPY packages/api-client/package.json ./packages/api-client/
COPY packages/shared/package.json ./packages/shared/
COPY packages/ui/package.json ./packages/ui/
COPY packages/validation/package.json ./packages/validation/
RUN pnpm install --frozen-lockfile || pnpm install

FROM deps AS build
ARG VITE_API_BASE_URL=""
ARG VITE_ENABLE_AI=false
ARG VITE_ENABLE_LLM=false
ARG VITE_ENABLE_IMPORTS=true
ARG VITE_ENABLE_ENTERPRISE=false
ARG VITE_ENABLE_CLIENT_PORTAL=false
ARG VITE_ENABLE_CLIENT_ENROLLMENT=false
ARG VITE_ENABLE_PORTAL_PUSH=false
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_ENABLE_AI=$VITE_ENABLE_AI
ENV VITE_ENABLE_LLM=$VITE_ENABLE_LLM
ENV VITE_ENABLE_IMPORTS=$VITE_ENABLE_IMPORTS
ENV VITE_ENABLE_ENTERPRISE=$VITE_ENABLE_ENTERPRISE
ENV VITE_ENABLE_CLIENT_PORTAL=$VITE_ENABLE_CLIENT_PORTAL
ENV VITE_ENABLE_CLIENT_ENROLLMENT=$VITE_ENABLE_CLIENT_ENROLLMENT
ENV VITE_ENABLE_PORTAL_PUSH=$VITE_ENABLE_PORTAL_PUSH
COPY . .
RUN pnpm --filter @verdin/shared build
RUN pnpm --filter @verdin/api-client build
RUN pnpm --filter @verdin/ui build
RUN pnpm --filter @verdin/validation build
RUN pnpm --filter @verdin/web build

FROM nginx:alpine AS production
COPY infrastructure/nginx/web.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/apps/web/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
