---
name: "ansible"
displayName: "Power Ansible"
description: "Build, lint, and validate Ansible playbooks and roles with best practices and idempotent design patterns."
keywords: ["ansible", "playbook", "handler", "ansible-role", "ansible-task", "ansible-lint", "ansible-inventory"]
author: "Max Bergmann"
---

# Ansible Power

## Overview

Complete Ansible automation toolkit with MCP tools for linting, validation, and playbook management. Includes comprehensive steering guides for roles, playbooks, inventory, vault, and collections.

`ansible-core` and `ansible-lint` are bundled as Python dependencies and installed automatically when the MCP server starts via `uvx`. No manual installation required.

---

## Onboarding

### Prerequisites
- [`uv`](https://docs.astral.sh/uv/) must be installed
- Python dependencies (`ansible-core`, `ansible-lint`, `mcp`) auto-install via `uvx` on first run

### Installation
Install via Kiro Powers Panel:
- **GitHub:** `https://github.com/bergmann-max/power-ansible`
- **Local:** Clone repo and add local directory path

### Configuration
No configuration required. Optional: Set `ANSIBLE_INVENTORY` environment variable for custom inventory path.

**Inventory resolution order:**
1. `ANSIBLE_INVENTORY` env var
2. `ansible.cfg` → `[defaults] inventory`
3. Fallback paths: `hosts.yml`, `hosts.yaml`, `hosts.ini`, `inventory/hosts.*`

---

## Available MCP Tools

| Tool | Purpose | Structured key | Auto-approved |
|------|---------|----------------|---------------|
| `lint_file` | Run ansible-lint on file or role directory | `findings[]` | ✅ |
| `syntax_check` | Validate playbook syntax without execution | `errors[]` | ✅ |
| `diff_check` | Preview changes with --check --diff mode | `recap{host}` | ❌ |
| `gather_facts` | Collect all facts from a host | `facts{}` | ❌ |
| `list_hosts` | Show hosts affected by playbook | `hosts[]` | ✅ |
| `list_tags` | List all tags in playbook | `tags[]` | ✅ |

**Return shape:** Every tool returns `{ok, stdout, stderr, <structured key>}`.
The structured key holds parsed output for LLM consumption — raw `stdout`/`stderr`
remain for debugging and when parsing fails.

**Workspace resolution:** Tools auto-resolve the workspace via the MCP `roots`
capability when the client advertises it. If `roots` is unavailable, pass
`project_root` as an absolute path on each call.

---

## When to Load Steering Files
- Ansible code style, idempotency, YAML, naming → `ansible-best-practices.md`
- Creating new role → `ansible-role-structure.md`
- Creating or running playbooks → `ansible-playbook-workflow.md`
- Setting up inventory, group_vars, host_vars → `ansible-inventory.md`
- Writing or tuning `ansible.cfg` (defaults, ssh, become, callbacks) → `ansible-config.md`
- Managing secrets or encrypted vars → `ansible-vault.md`
- Installing or using Galaxy collections → `ansible-collections.md`

---

## Available Steering Files

Guides for Ansible workflows and best practices:

- **ansible-best-practices.md** - Core patterns, idempotency, YAML style, naming conventions
- **ansible-role-structure.md** - Role directory layout, task organization, handlers, defaults
- **ansible-playbook-workflow.md** - Playbook creation, execution patterns, play structure
- **ansible-inventory.md** - Inventory structure, group_vars, host_vars, dynamic inventory
- **ansible-config.md** - `ansible.cfg` defaults, SSH, privilege escalation, callbacks, plugins
- **ansible-vault.md** - Secrets management with Ansible Vault, encryption patterns
- **ansible-collections.md** - Galaxy collections, requirements.yml, namespace management

---

## Workflows

### Creating a new Playbook
1. Ask which hosts/groups should be targeted and what tasks should be performed
2. Write the playbook file directly to `playbooks/<name>.yml` using your file tools
3. Follow the structure in the steering file `ansible-playbook-workflow.md`
4. Lint with `lint_file(path="/path/to/playbook.yml", project_root="/project/root")`
5. Run syntax check with `syntax_check(playbook="/path/to/playbook.yml", project_root="/project/root")`

### Creating a new Role
1. Write all role files directly using your file tools:
   - `roles/<name>/tasks/main.yml`
   - `roles/<name>/handlers/main.yml`
   - `roles/<name>/defaults/main.yml`
   - `roles/<name>/vars/main.yml`
   - `roles/<name>/meta/main.yml`
   - `roles/<name>/README.md`
   - `roles/<name>/templates/` and `roles/<name>/files/` (empty dirs via `.gitkeep`)
2. Follow the structure in the steering file `ansible-role-structure.md`
3. Lint the entire role directory with `lint_file(path="/path/to/roles/<name>", project_root="/project/root")`

### Validating Playbook Design
1. **Verify host targeting:**
   - Use `list_hosts(playbook="/path/to/playbook.yml", project_root="/project/root")`
   - Confirms playbook targets the intended hosts/groups
   - Optionally test with limit: `list_hosts(..., limit="webservers")` or `limit="web01.example.com"`
2. **Validate playbook logic (dry-run):**
   - Use `diff_check(playbook="/path/to/playbook.yml", project_root="/project/root")`
   - Shows what would change without applying anything
   - Catches logic errors and unintended side effects
   - Optionally limit scope: `diff_check(..., limit="staging")`

### Working with Tags
1. **List all available tags:**
   - Use `list_tags(playbook="/path/to/playbook.yml", project_root="/project/root")`
   - Shows all tags defined in the playbook
2. **Document tag usage patterns:**
   - Tags allow selective task execution
   - Common patterns: deployment stages, component groups, environment-specific tasks
   - Example tag organization: `deploy`, `config`, `backup`, `rollback`

### Gathering Host Information
1. **Collect facts from a host or group:**
   - Use `gather_facts(host="webservers", project_root="/project/root")`
   - Or specific host: `gather_facts(host="web01.example.com", project_root="/project/root")`
2. **Use cases for playbook development:**
   - Verify host connectivity before writing tasks
   - Check available facts (ansible_distribution, ansible_os_family, network interfaces)
   - Design conditional tasks based on actual host properties

### Troubleshooting Playbook Development
1. **Syntax errors:**
   - Run `syntax_check` — catches YAML and Ansible syntax issues
   - Fix reported errors before validation
2. **Linting failures:**
   - Run `lint_file` — catches best practice violations
   - Review ansible-lint output for rule violations (e.g., `name[missing]`, `yaml[line-length]`)
   - Fix violations to ensure idempotent, maintainable playbooks
3. **Unexpected logic in dry-run:**
   - Run `diff_check` to validate playbook behavior
   - Compare expected vs. actual changes
   - Refine tasks if logic doesn't match intent
4. **Host targeting issues:**
   - Use `list_hosts` to verify correct hosts are targeted
   - Check inventory configuration if hosts missing or wrong
5. **Variable and fact issues:**
   - Use `gather_facts` to inspect available host facts
   - Verify `group_vars/` and `host_vars/` for variable conflicts
   - Check fact names match what tasks expect

### Creating ansible.cfg
1. Write `ansible.cfg` at the project root using your file tools
2. Follow the structure and section reference in `ansible-config.md`
3. Audit applied values with `ansible-config dump --only-changed`

### Creating Inventory
1. Write `inventory/hosts.yml` (or `hosts.ini`) using your file tools
2. Follow the structure in `ansible-inventory.md` (groups, group_vars, host_vars)
3. Verify inventory with `list_hosts` on any playbook

---

## Troubleshooting

### MCP Server Won't Start

**Symptom:** Power-ansible tools unavailable, MCP server shows as disconnected in Kiro.

**Cause: `uv` / `uvx` not installed**
```
Error: command not found: uvx
```
Solution: Install `uv` — https://docs.astral.sh/uv/getting-started/installation/
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or via pip
pip install uv
```
After install, reconnect the MCP server from the Kiro MCP Server panel.

**Cause: Python version too old**
```
Error: requires Python >=3.10
```
Solution: `uvx` picks the system Python. Install Python 3.10+ and ensure it is on `PATH`, or set `UV_PYTHON` env var:
```bash
UV_PYTHON=python3.11 uvx ansible-mcp
```

**Cause: Git not installed (GitHub source install)**
```
Error: failed to clone repository
```
Solution: Install git and ensure it is on `PATH`.

---

### First-Run Dependency Install Fails

**Symptom:** First tool call hangs or fails with pip/build errors.

`uvx` downloads and installs `ansible-core`, `ansible-lint`, and `mcp` on first run. This requires internet access and may take 30–60 seconds.

- Check internet connectivity
- Check for corporate proxy: set `HTTP_PROXY` / `HTTPS_PROXY` env vars in `mcp.json`
- Re-trigger by reconnecting the MCP server from the Kiro MCP Server panel

---

### Tool Call Returns "Workspace not resolved"

**Symptom:**
```
Error: Workspace not resolved. Either the client must advertise the MCP
'roots' capability, or pass project_root as an absolute path.
```

The MCP client did not expose a workspace via `roots`, and no `project_root`
argument was passed. Resolution:

- If your client supports MCP roots, ensure exactly one workspace folder is
  open and re-run.
- Otherwise pass `project_root` as an **absolute path** to an existing Ansible
  workspace directory (relative paths and unresolved `${workspaceFolder}`
  placeholders are rejected).

---

### `lint_file` Reports No Rules / Empty Output

**Cause:** No `.ansible-lint` config found — ansible-lint falls back to minimal profile.

Solution: Add `.ansible-lint` to the project root. Minimal config:
```yaml
profile: production
offline: true
```
See `ansible-best-practices.md` for full recommended config.

---

### `syntax_check` Passes but `lint_file` Fails

Expected behavior — `syntax_check` only validates YAML structure and Ansible syntax. `lint_file` enforces best-practice rules (FQCN, idempotency, naming). Fix lint violations before considering a playbook production-ready.

---

### `diff_check` / `gather_facts` Require SSH Access

`diff_check` and `gather_facts` connect to real hosts. Ensure:
- SSH key or password auth is configured
- `ansible_user` is set in inventory or `ansible.cfg`
- Target hosts are reachable from the machine running Kiro
