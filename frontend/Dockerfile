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

# Production stage - use node to serve
FROM node:20-alpine

WORKDIR /app

# Install serve globally
RUN npm install -g serve@14

# Copy built files
COPY --from=builder /app/dist ./dist

# Railway provides PORT env variable
ENV PORT=3000

EXPOSE 3000

# Use exec form with shell to expand PORT variable
CMD sh -c "serve -s dist -l tcp://0.0.0.0:$PORT"
