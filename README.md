# Kiro Power: Ansible

![Kiro Power](https://img.shields.io/badge/kiro-power-9046FF)
![MCP](https://img.shields.io/badge/MCP-FastMCP-5468FF)
![uvx](https://img.shields.io/badge/uvx-ready-lightgrey)
![Ansible](https://img.shields.io/badge/ansible--core-2.20-red)
![ansible-lint](https://img.shields.io/badge/ansible--lint-25.6-yellow)
![License](https://img.shields.io/badge/license-Unlicense-green)

Build, lint, and validate Ansible playbooks and roles with best practices, proper structure, and idempotent design patterns.

A [Kiro Power](https://kiro.dev) that provides an MCP server, steering files, and hooks for Ansible development.

## Prerequisites

[`uv`](https://docs.astral.sh/uv/) must be installed — that's it. All Python dependencies are managed automatically on first start.

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Arch Linux
sudo pacman -S uv
```

Python dependencies (installed automatically via `uvx`):
- `mcp[cli] >= 1.26.0`
- `ansible-core >= 2.20.0`
- `ansible-lint >= 25.6.0`

## Installation

### Option A – Via GitHub (recommended)
In Kiro: Powers Panel → "Import from GitHub"
```
https://github.com/bergmann-max/power-ansible
```

### Option B – Install locally
```bash
cp -r power-ansible ~/.kiro/powers/installed/ansible-mcp
```
Then in Kiro: Powers Panel → "Install from local path"

## Activation

The power activates automatically when you use terms like `ansible`, `playbook`, `role`, `inventory`, `task`, `handler`, `vars`, `yaml`, `automation`, `infrastructure`.

## MCP Tools

| Tool | Description |
|---|---|
| `create_playbook` | Scaffold a new playbook with FQCN, tags, and pre_tasks |
| `create_role` | Create a complete role structure (tasks, handlers, defaults, vars, meta, templates, files) |
| `scaffold_inventory` | Create an inventory with hosts.ini and group_vars |
| `create_ansible_cfg` | Create ansible.cfg with sensible defaults |
| `lint_file` | Run ansible-lint with production profile on a file or directory |
| `syntax_check` | Check playbook syntax without executing |
| `diff_check` | Dry-run with `--check --diff` to preview changes |
| `gather_facts` | Collect all facts from a host via the setup module |
| `list_playbooks` | List all playbooks in the project |
| `list_roles` | List all local roles |
| `show_role_tree` | Display the file structure of a role |

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ANSIBLE_PROJECT_ROOT` | `cwd` | Root of the Ansible project |
| `ANSIBLE_INVENTORY` | auto-detected | Path to inventory file |

Inventory is resolved in this order: `ANSIBLE_INVENTORY` env var → `ansible.cfg [defaults] inventory` → common fallback paths (`hosts.yml`, `hosts.ini`, `inventory/hosts.yml`, `inventory/hosts.ini`).

## Steering Files

| File | When active | Content |
|---|---|---|
| `ansible-best-practices.md` | Always | FQCN, idempotency, variables, lint rules |
| `ansible-playbook-workflow.md` | For playbook files | Playbook creation workflow |
| `ansible-role-structure.md` | For role files | Role structure and conventions |
| `ansible-inventory.md` | For inventory files | Inventory layout and group_vars |

## Hooks

| Hook | Trigger | Action |
|---|---|---|
| `ansible-lint-on-save` | Save `playbooks/**/*.yml`, `roles/**/tasks/*.yml`, `roles/**/handlers/*.yml` | Runs `lint_file` and shows errors with explanations |

## Project Structure

```
power-ansible/
├── POWER.md                              # Kiro Power manifest
├── mcp.json                              # MCP server configuration
├── pyproject.toml                        # Package definition for uvx
├── ansible_mcp/
│   └── server.py                         # FastMCP server implementation
├── hooks/
│   └── ansible-lint-on-save.kiro.hook   # Auto-lint on file save
└── steering/
    ├── ansible-best-practices.md         # Always loaded
    ├── ansible-playbook-workflow.md      # Only for playbooks
    ├── ansible-role-structure.md         # Only for roles
    └── ansible-inventory.md             # Only for inventory
```
