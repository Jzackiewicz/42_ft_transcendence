# NGINX Documentation: https://nginx.org/en/docs/
# NGINX Hub Image: https://hub.docker.com/_/nginx
# Alpine Linux Package Keeper (APK): https://wiki.alpinelinux.org/wiki/Alpine_Package_Keeper

FROM nginx:1.25.5-alpine3.19

# Install OpenSSL for self-signed certificates
RUN apk add --no-cache openssl

# Remove default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom configuration
COPY devops/nginx/nginx.conf /etc/nginx/conf.d/

# Generate self-signed SSL certificate (for development/defense)
RUN mkdir -p /etc/nginx/ssl && \
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
	-keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt \
	-subj "/C=FR/ST=Paris/L=Paris/O=42/OU=Quizscendence/CN=localhost"

# Expose ports
EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
