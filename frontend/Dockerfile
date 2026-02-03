FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .

# Build with environment variable support
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Create nginx config template
RUN echo 'server { \
    listen PORT_PLACEHOLDER; \
    listen [::]:PORT_PLACEHOLDER; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf.template

EXPOSE 80

# Replace PORT placeholder and start nginx
CMD sh -c "sed 's/PORT_PLACEHOLDER/'\"${PORT:-80}\"'/g' /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
