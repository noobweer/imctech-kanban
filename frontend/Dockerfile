FROM oven/bun:1.3-alpine AS development
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install
COPY . .

FROM development AS builder
RUN bun run build

FROM nginx:stable-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html