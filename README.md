# Kiro Power: Ansible

[![Kiro Power](https://img.shields.io/badge/kiro-power-8B43E8?logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNMTUuMjUgMi40NUMxNC4zMiAyLjA4IDEzLjIzIDEuOTcgMTIuMzIgMi4wMEMxMS40MSAyLjAzIDEwLjUyIDIuMzAgOS43NyAyLjY0QzkuMDIgMi45OCA4LjM4IDMuNDAgNy44MCA0LjA0QzcuMjEgNC42OCA2LjcwIDQuOTkgNi4yNyA2LjQ2QzUuODMgNy45MiA1LjYwIDExLjEyIDUuMTggMTIuODNDNC43NyAxNC41NCAzLjk2IDE1Ljk0IDMuNzggMTYuNzFDMy42MCAxNy40OSAzLjkyIDE3LjI5IDQuMTAgMTcuNDhDNC4yOCAxNy42NyA0LjQwIDE3Ljg1IDQuODcgMTcuODZDNS4zMyAxNy44NyA2LjY0IDE3LjE2IDYuOTAgMTcuNTRDNy4xNyAxNy45MiA2LjQ2IDE5LjU2IDYuNDYgMjAuMTVDNi40NiAyMC43NSA2LjY3IDIwLjg0IDYuOTAgMjEuMTFDNy4xNCAyMS4zNyA3LjM1IDIxLjYzIDcuODYgMjEuNzVDOC4zNyAyMS44NiA5LjE5IDIyLjAyIDkuOTYgMjEuODFDMTAuNzQgMjEuNjAgMTEuOTIgMjAuNDcgMTIuNTEgMjAuNDdDMTMuMTAgMjAuNDcgMTMuMDcgMjEuNjAgMTMuNTMgMjEuODFDMTMuOTkgMjIuMDIgMTQuNTcgMjIuMDUgMTUuMjUgMjEuNzVDMTUuOTMgMjEuNDQgMTYuOTcgMjAuNjkgMTcuNjEgMTkuOTZDMTguMjQgMTkuMjMgMTguNjUgMTguNTkgMTkuMDcgMTcuMzVDMTkuNDkgMTYuMTEgMjAuMDYgMTQuMTkgMjAuMTUgMTIuNTFDMjAuMjUgMTAuODMgMjAuMDMgOC42OCAxOS42NCA3LjI5QzE5LjI2IDUuOTAgMTguNTkgNC45NyAxNy44NiA0LjE3QzE3LjEzIDMuMzYgMTYuMTcgMi44MSAxNS4yNSAyLjQ1Wk0xNS4yNCA5LjEyQTEuMDcgMS42NyAwLjIgMSAxIDE3LjM5IDkuMTJBMS4wNyAxLjY3IDAuMiAxIDEgMTUuMjQgOS4xMlpNMTMuOTkgOS4xMkExLjA3IDEuNjcgMTc5LjkgMSAxIDExLjg1IDkuMTJBMS4wNyAxLjY3IDE3OS45IDEgMSAxMy45OSA5LjEyWiIvPjwvc3ZnPg==&logoColor=white&style=for-the-badge)](https://kiro.dev/docs/powers/)
[![Version](https://img.shields.io/github/v/tag/bergmann-max/power-ansible?label=version&color=green&sort=semver&style=for-the-badge)](https://github.com/bergmann-max/power-ansible/tags)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](https://github.com/bergmann-max/power-ansible/blob/main/LICENSE)

[Kiro Power](https://kiro.dev/docs/powers/) that provides an MCP server and steering files to build, lint, and validate Ansible playbooks and roles with best practices.

## MCP Tools

- `lint_file` - ansible-lint on file or role directory
- `syntax_check` - validate playbook syntax without execution
- `diff_check` - preview changes via `--check --diff`
- `gather_facts` - collect facts from a host via setup module
- `list_hosts` - list hosts affected by playbook
- `list_tags` - list tags defined in playbook

## Steering Files

- `ansible-best-practices.md` - core patterns, idempotency, YAML style, naming
- `ansible-role-structure.md` - role layout, task organization, handlers, defaults
- `ansible-playbook-workflow.md` - playbook creation, execution, play structure
- `ansible-jinja.md` - Jinja2 filters, tests, lookups
- `ansible-inventory.md` - inventory structure, group_vars, host_vars, dynamic inventory
- `ansible-config.md` - `ansible.cfg` defaults, SSH, privilege escalation, callbacks, plugins
- `ansible-vault.md` - secrets management, encryption patterns
- `ansible-collections.md` - Galaxy collections, requirements.yml, namespaces

## Prerequisites

Requires [`uv`](https://docs.astral.sh/uv/) and Python 3.12+. Dependencies (`ansible-core>=2.20`, `ansible-lint>=25.6`, `fastmcp>=3`) are resolved by `uvx`.

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

```text
https://github.com/bergmann-max/power-ansible
```

**Via Local Directory:**

```bash
git clone https://github.com/bergmann-max/power-ansible.git
```

Then in Kiro Powers Panel → "Add Custom Power" → "Local Directory" → provide path

## Activation

Kiro loads this Power's MCP tools and steering files into context whenever your chat message contains one of these keywords:

```text
ansible, playbook, role, handler, inventory, vault
```

## Slash Commands

This power ships 3 slash commands (manual trigger hooks), installed automatically on first power use via the onboarding in [POWER.md](POWER.md#onboarding):

| Command | Steering file(s) | What it does |
|---------|-------------------|-------------|
| `/ansible-new-role` | `ansible-role-structure.md` | Scaffold a complete role directory |
| `/ansible-new-playbook` | `ansible-playbook-workflow.md` | Scaffold a playbook with correct skeleton |
| `/ansible-fix-lint` | `ansible-best-practices.md` | Auto-fix mechanical ansible-lint violations |


See [POWER.md](POWER.md#onboarding) for details.

## Documentation

See [POWER.md](POWER.md) for workflows, tool argument reference, and troubleshooting.

## License

[MIT](LICENSE)

## Author

Max Bergmann
