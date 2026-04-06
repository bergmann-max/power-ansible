# Kiro Power - Ansible

Build, lint, and validate Ansible playbooks and roles with best practices, proper structure, and idempotent design patterns.

## Prerequisites

[`uv`](https://docs.astral.sh/uv/) must be installed — that's it. All Python dependencies are managed automatically on first start.

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Arch Linux
sudo pacman -S uv
```

## Installation

### Option A – Via GitHub (recommended)
In Kiro: **Powers Panel → "Import from GitHub"**
```
https://github.com/bergmann-max/power-ansible
```

### Option B – Install locally
```bash
cp -r power-ansible ~/.kiro/powers/installed/ansible
```
Then in Kiro: **Powers Panel → "Install from local path"**

## Activation

The power activates automatically when you use terms like **ansible**, **playbook**, **role**, **inventory**, **task**, **handler**.

## MCP Tools

| Tool | Description |
|---|---|
| `create_playbook` | Scaffold a new playbook |
| `create_role` | Create a complete role structure |
| `scaffold_inventory` | Create an inventory with group_vars |
| `create_ansible_cfg` | Create ansible.cfg with defaults |
| `lint_file` | Run ansible-lint |
| `syntax_check` | Check playbook syntax |
| `diff_check` | Dry-run with --diff to preview file changes |
| `gather_facts` | Collect all facts from a host via setup module |
| `list_playbooks` | List all playbooks in the project |
| `list_roles` | List all local roles |
| `show_role_tree` | Display the file structure of a role |

## Steering Files

| File | When active |
|---|---|
| `ansible-best-practices.md` | Always (FQCN, idempotency, variables) |
| `ansible-playbook-workflow.md` | For playbook files |
| `ansible-role-structure.md` | For role files |
| `ansible-inventory.md` | For inventory files |

## Project Structure

```
power-ansible/
├── POWER.md                              # Kiro Power Manifest
├── mcp.json                              # MCP Server Configuration
├── pyproject.toml                        # Package definition for uvx
├── ansible_mcp/
│   └── server.py                         # Packaged MCP server (FastMCP)
├── hooks/
│   └── ansible-lint-on-save.kiro.hook   # Auto-lint on file change
└── steering/
    ├── ansible-best-practices.md         # Always loaded
    ├── ansible-playbook-workflow.md      # Only for playbooks
    ├── ansible-role-structure.md         # Only for roles
    └── ansible-inventory.md             # Only for inventory
```
