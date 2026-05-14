# Kiro Power: Ansible

[![Version](https://img.shields.io/github/v/tag/bergmann-max/power-ansible?label=version&color=blue&sort=semver)](https://github.com/bergmann-max/power-ansible/tags)
[![Kiro Power](https://img.shields.io/badge/kiro-power-9046FF)](https://kiro.dev/docs/powers/)
[![FastMCP](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/bergmann-max/power-ansible/main/pyproject.toml&query=%24.project.dependencies%5B0%5D&label=fastmcp&color=5468FF&logo=python&logoColor=white)](https://github.com/jlowin/fastmcp)
[![Ansible](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/bergmann-max/power-ansible/main/pyproject.toml&query=%24.project.dependencies%5B1%5D&label=ansible--core&color=red&logo=ansible&logoColor=white)](https://docs.ansible.com/projects/ansible)
[![ansible-lint](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/bergmann-max/power-ansible/main/pyproject.toml&query=%24.project.dependencies%5B2%5D&label=ansible--lint&color=yellow&logo=ansible&logoColor=white)](https://docs.ansible.com/projects/lint/)
[![License](https://img.shields.io/badge/license-MIT-blue?)](https://github.com/bergmann-max/power-ansible/blob/main/LICENSE)

A [Kiro Power](https://kiro.dev/docs/powers/) that provides an MCP server and steering files to build, lint, and validate Ansible playbooks and roles.

## MCP Tools

- `lint_file` — ansible-lint on file or role directory
- `syntax_check` — validate playbook syntax without execution
- `diff_check` — preview changes via `--check --diff`
- `gather_facts` — collect facts from a host via setup module
- `list_hosts` — list hosts affected by playbook
- `list_tags` — list tags defined in playbook

## Steering Files

- `ansible-best-practices.md` — core patterns, idempotency, YAML style, naming
- `ansible-role-structure.md` — role layout, task organization, handlers, defaults
- `ansible-playbook-workflow.md` — playbook creation, execution, play structure
- `ansible-inventory.md` — inventory structure, group_vars, host_vars, dynamic inventory
- `ansible-config.md` — `ansible.cfg` defaults, SSH, privilege escalation, callbacks, plugins
- `ansible-vault.md` — secrets management, encryption patterns
- `ansible-collections.md` — Galaxy collections, requirements.yml, namespaces

## Prerequisites

[`uv`](https://docs.astral.sh/uv/) must be installed. Python dependencies (`ansible-core`, `ansible-lint`, `mcp`) auto-install via `uvx` on first run.

**Install uv:**
```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

**Via GitHub (recommended):**

In Kiro Powers Panel → "Add Custom Power" → "Git Repository"
```
https://github.com/bergmann-max/power-ansible
```

**Via Local Directory:**
```bash
git clone https://github.com/bergmann-max/power-ansible.git
```
Then in Kiro Powers Panel → "Add Custom Power" → "Local Directory" → provide path

## Configuration

No configuration required. Optional: set `ANSIBLE_INVENTORY` for custom inventory path.

Inventory resolution order:
1. `ANSIBLE_INVENTORY` env var
2. `ansible.cfg` → `[defaults] inventory`
3. Fallback paths: `hosts.yml`, `hosts.yaml`, `hosts.ini`, `inventory/hosts.*`

## Documentation

See [POWER.md](POWER.md) for workflows, tool argument reference, and troubleshooting.
