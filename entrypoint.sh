#!/bin/bash
# Restore .claude.json from backup if missing
CLAUDE_JSON="$HOME/.claude.json"
BACKUP_DIR="$HOME/.claude/backups"

if [ ! -f "$CLAUDE_JSON" ] && [ -d "$BACKUP_DIR" ]; then
    LATEST=$(ls -t "$BACKUP_DIR"/.claude.json.backup.* 2>/dev/null | head -1)
    if [ -n "$LATEST" ]; then
        cp "$LATEST" "$CLAUDE_JSON"
    fi
fi

exec claude "$@"
