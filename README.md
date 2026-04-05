# Kiro Power - Ansible

Full Ansible tooling for Kiro: scaffold, lint, syntax-check, and diff playbooks & roles.

## Installation

### Option A – Install locally (recommended for development)
```bash
# Copy the power folder into the Kiro powers directory
cp -r power-ansible ~/.kiro/powers/installed/ansible
```
Then in Kiro: **Powers Panel → "Install from local path"**

### Option B – Via GitHub
```
https://github.com/bergmann-max/power-ansible
```
In Kiro: **Powers Panel → "Import from GitHub"**

## Prerequisites

Create a virtual environment inside the repo (required for `mcp.json` to work):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

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
├── mcp_server.py                         # MCP Server (Python/FastMCP)
├── requirements.txt                      # Python dependencies
├── .venv/                                # Local virtualenv (not committed)
├── hooks/
│   └── ansible-lint-on-save.kiro.hook   # Auto-lint on file change
└── steering/
    ├── ansible-best-practices.md         # Always loaded
    ├── ansible-playbook-workflow.md      # Only for playbooks
    ├── ansible-role-structure.md         # Only for roles
    └── ansible-inventory.md             # Only for inventory
```
