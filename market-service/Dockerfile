# Build and compile dependencies
FROM node:20-alpine AS builder
WORKDIR /workspace

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Runtime environment
FROM node:20-alpine as runner
WORKDIR /app

# Copy package files
COPY --from=builder /workspace/node_modules ./node_modules
COPY . .

# Environment setup
ENV NODE_ENV=production

# Start app
CMD ["node", "app.js"]