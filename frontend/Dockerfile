FROM oven/bun:1 AS base
WORKDIR /app

# Install dependencies
COPY package.json ./
COPY bun.lockb* ./
RUN bun install

# Copy source
COPY . .

# Expose port
EXPOSE 5173

# Start dev server
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]