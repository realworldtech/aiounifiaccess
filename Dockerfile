FROM node:22-bookworm-slim

RUN apt-get update && apt-get install -y \
    git \
    ripgrep \
    ca-certificates \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code globally
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user
RUN useradd -m -s /bin/bash claude

# Create workspace directory
RUN mkdir -p /workspace && chown claude:claude /workspace

# Create .claude directory for credential persistence
RUN mkdir -p /home/claude/.claude && chown claude:claude /home/claude/.claude

# Entrypoint that restores .claude.json from backup if missing
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

USER claude
WORKDIR /workspace

ENTRYPOINT ["entrypoint.sh"]
