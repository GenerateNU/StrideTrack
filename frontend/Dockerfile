FROM oven/bun:1 AS base
WORKDIR /app

# Copy dependency files
COPY package.json ./
COPY bun.lock* ./

# Copy source
COPY . .

# Expose port
EXPOSE 5173

# Install deps and start dev server (install on startup for dev)
CMD ["sh", "-c", "bun install && bun run dev --host 0.0.0.0"]