#!/usr/bin/env bash
# Wrapper: runs the MCP server via uvx from the script's own directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uvx --from "$SCRIPT_DIR" power-ansible
