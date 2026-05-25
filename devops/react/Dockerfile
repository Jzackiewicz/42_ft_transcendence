# Node Hub Image: https://hub.docker.com/_/node
# Docker Multi-stage Builds: https://docs.docker.com/build/building/multi-stage/
# Vite Deployment: https://vitejs.dev/guide/static-deploy.html

# Stage 1: Build
FROM node:26.2.0-alpine3.22 AS build

WORKDIR /app

# Copy package files
COPY client/package*.json ./

# Install dependencies
# uses npm ci for reproducable builds instead of npm istall
RUN npm ci

# Copy source
COPY client/ ./

# Build project
RUN npm run build

# Stage 2: Serve
# In production, we serve with NGINX. 
# For consistency with the roadmap, we can use a small alpine image 
# to hold the assets, or just use the node image if we're in dev mode.
# Roadmap step 2 says "Multi-stage build to serve static files with NGINX".
FROM nginx:1.25.5-alpine3.19

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Configure NGINX to serve the SPA and fall back to index.html for deep links
RUN printf '%s\n' \
	'server {' \
	'    listen 80;' \
	'    server_name _;' \
	'    root /usr/share/nginx/html;' \
	'    index index.html;' \
	'' \
	'    location / {' \
	'        try_files $uri $uri/ /index.html;' \
	'    }' \
	'}' > /etc/nginx/conf.d/default.conf

# Default NGINX port
EXPOSE 80
# EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]
