# Stage 1: Backend dependencies and code
FROM python:3.11-slim AS backend
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./

# Stage 2: Frontend dependencies and build
FROM node:18 AS frontend
WORKDIR /frontend
COPY package.json ./
COPY pnpm-lock.yaml ./
COPY components/ ./components/
COPY public/ ./public/
COPY styles/ ./styles/
COPY tailwind.config.ts ./
COPY postcss.config.mjs ./
COPY tsconfig.json ./
COPY next.config.mjs ./
COPY src/ ./src/
COPY app/ ./app/
COPY lib/ ./lib/
RUN npm install
RUN npm run build

# Stage 3: Final image
FROM python:3.11-slim
WORKDIR /app
# Copy backend
COPY --from=backend /app /app
# Copy frontend build
COPY --from=frontend /frontend/.next /app/frontend/.next
COPY --from=frontend /frontend/public /app/frontend/public
COPY --from=frontend /frontend/package.json /app/frontend/package.json
COPY --from=frontend /frontend/next.config.mjs /app/frontend/next.config.mjs
COPY --from=frontend /frontend/tsconfig.json /app/frontend/tsconfig.json
COPY --from=frontend /frontend/tailwind.config.ts /app/frontend/tailwind.config.ts
COPY --from=frontend /frontend/postcss.config.mjs /app/frontend/postcss.config.mjs
# Install Node.js for serving frontend
RUN apt-get update && apt-get install -y nodejs npm
WORKDIR /app/frontend
RUN npm install --production
WORKDIR /app
# Install supervisor
RUN apt-get update && apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
EXPOSE 10000
CMD ["/usr/bin/supervisord"]
