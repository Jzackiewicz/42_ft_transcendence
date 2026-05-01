# NGINX Documentation: https://nginx.org/en/docs/
# NGINX Hub Image: https://hub.docker.com/_/nginx
# Alpine Linux Package Keeper (APK): https://wiki.alpinelinux.org/wiki/Alpine_Package_Keeper

FROM nginx:1.25.5-alpine3.19

# Install OpenSSL for self-signed certificates
RUN apk add --no-cache openssl

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom configuration template
COPY devops/nginx/nginx.conf.template /etc/nginx/templates/nginx.conf.template

# Generate self-signed SSL certificate (for development/defense)
RUN mkdir -p /etc/nginx/ssl && \
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
	-keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt \
	-subj "/C=FR/ST=Paris/L=Paris/O=42/OU=Quizscendence/CN=localhost"

# Expose ports
EXPOSE 80 443

# envsubst is built-in in nginx official docker image entrypoint for .template files in /etc/nginx/templates/
# See: https://hub.docker.com/_/nginx "Using environment variables in nginx configuration"
CMD ["nginx", "-g", "daemon off;"]
