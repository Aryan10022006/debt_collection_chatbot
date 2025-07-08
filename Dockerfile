# Stage 1: Backend dependencies and code
FROM python:3.11-slim AS backend
WORKDIR /app
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./

# Stage 2: Frontend dependencies and build
FROM node:18 AS frontend
WORKDIR /frontend
COPY app/ ./
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
