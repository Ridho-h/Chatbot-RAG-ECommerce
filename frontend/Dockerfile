# ── Frontend Dockerfile ───────────────────────────────────────────────
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config for SPA routing + API proxy
RUN echo 'server { \
    listen 3000; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    location /api { \
        proxy_pass http://backend:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_read_timeout 120s; \
        proxy_connect_timeout 120s; \
        proxy_send_timeout 120s; \
    } \
    \
    location /health { \
        proxy_pass http://backend:8000; \
    } \
    \
    location /ready { \
        proxy_pass http://backend:8000; \
    } \
    \
    location /docs { \
        proxy_pass http://backend:8000; \
    } \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
