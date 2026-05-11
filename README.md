# Kiro Power: Ansible

[![Kiro Power](https://img.shields.io/badge/kiro-power-9046FF)](https://kiro.dev/docs/powers/)
[![FastMCP](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/bergmann-max/power-ansible/main/pyproject.toml&query=%24.project.dependencies%5B0%5D&label=fastmcp&color=5468FF&logo=python&logoColor=white)](https://github.com/jlowin/fastmcp)
[![Ansible](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/bergmann-max/power-ansible/main/pyproject.toml&query=%24.project.dependencies%5B1%5D&label=ansible--core&color=red&logo=ansible&logoColor=white)](https://docs.ansible.com/projects/ansible)
[![ansible-lint](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/bergmann-max/power-ansible/main/pyproject.toml&query=%24.project.dependencies%5B2%5D&label=ansible--lint&color=yellow&logo=ansible&logoColor=white)](https://docs.ansible.com/projects/lint/)
[![License](https://img.shields.io/badge/license-Unlicense-green?logo=unlicense&logoColor=white)](https://github.com/bergmann-max/power-ansible/blob/main/LICENSE)

A [Kiro Power](https://kiro.dev/docs/powers/) that provides an MCP server and steering files for build, lint, and validate Ansible playbooks and roles with best practices.

## Prerequisites

[`uv`](https://docs.astral.sh/uv/) must be installed. Python dependencies (`ansible-core`, `ansible-lint`, `mcp`) auto-install via `uvx`.

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

## Documentation

See [POWER.md](POWER.md) for:
- Available MCP tools and workflows
- Steering files (best practices, role structure, playbook workflow, inventory, vault, collections)
- Configuration options
- Troubleshooting

## Quick Reference

**MCP Tools:** `lint_file`, `syntax_check`, `diff_check`, `gather_facts`, `list_hosts`, `list_tags`

**Steering Files:** `ansible-best-practices.md`, `ansible-role-structure.md`, `ansible-playbook-workflow.md`, `ansible-inventory.md`, `ansible-vault.md`, `ansible-collections.md`
