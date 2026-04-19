# Kiro Power: Ansible

[![Kiro Power](https://img.shields.io/badge/kiro-power-9046FF)](https://kiro.dev/)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-5468FF)](https://modelcontextprotocol.io/)
[![Ansible](https://img.shields.io/badge/ansible--core-2.20-red)](https://docs.ansible.com/projects/ansible)
[![ansible-lint](https://img.shields.io/badge/ansible--lint-25.6-yellow)](https://docs.ansible.com/projects/lint/)
[![License](https://img.shields.io/badge/license-Unlicense-green)](https://github.com/bergmann-max/power-ansible/blob/main/LICENSE)

Build, lint, and validate Ansible playbooks and roles with best practices, proper structure, and idempotent design patterns.

A [Kiro Power](https://kiro.dev) that provides an MCP server and steering files for Ansible development.

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

The power activates automatically when you use terms like `ansible`, `playbook`, `role`, `inventory`, `task`, `handler`, `vars`, `yaml`, `automation`, `infrastructure`, `idempotent`, `hosts`, `galaxy`, `collections`.

## MCP Tools

| Tool | Description |
|---|---|
| `lint_file` | Run ansible-lint with production profile on a file or directory |
| `syntax_check` | Check playbook syntax without executing |
| `diff_check` | Dry-run with `--check --diff` to preview changes |
| `gather_facts` | Collect all facts from a host via the setup module |
| `list_hosts` | Show which hosts would be affected by a playbook |
| `list_tags` | Show all tags defined in a playbook |

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ANSIBLE_INVENTORY` | auto-detected | Override inventory |

Inventory is resolved in this order: `ANSIBLE_INVENTORY` env var → `ansible.cfg [defaults] inventory` → common fallback paths (`hosts.yml`, `hosts.yaml`, `hosts.ini`, `inventory/hosts.yml`, `inventory/hosts.yaml`, `inventory/hosts.ini`).

## Steering Files

| File | When active | Content |
|---|---|---|
| `ansible-best-practices.md` | Always | Core principles, patterns, and module reference |
| `ansible-playbook-workflow.md` | For playbook files | Playbook creation workflow |
| `ansible-role-structure.md` | For role files | Role structure and conventions |
| `ansible-inventory.md` | For inventory files | Inventory layout and group_vars |
| `ansible-vault.md` | For vault files | Secret management with ansible-vault |
| `ansible-collections.md` | For requirements.yml | Community collections and Galaxy |

## Troubleshooting

### MCP tools not working
1. Check server is running: `uvx ansible-mcp`
2. Verify in Kiro: MCP Server view → ansible server status
3. Check logs: stderr output in MCP panel
4. Restart server: Powers Panel → ansible → Reconnect

### Inventory not found
Set explicitly via environment variable:
```bash
export ANSIBLE_INVENTORY=inventory/hosts.yml
```

Or configure in `ansible.cfg`:
```ini
[defaults]
inventory = inventory/hosts.yml
```

### ansible-lint errors
Run manually to see full output:
```bash
ansible-lint --profile production playbooks/
```

Check `.ansible-lint` config if rules need adjustment.

### Connection issues
Test connectivity:
```bash
ansible all -m ping -i inventory/hosts.yml
```

Common fixes:
- Set `ansible_user` in inventory or group_vars
- Verify SSH key: `ansible_ssh_private_key_file`
- Add `become: true` for privilege escalation
