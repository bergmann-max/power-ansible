---
name: "ansible"
displayName: "Power Ansible"
author: "Max Bergmann"
description: "Build, lint, and validate Ansible playbooks and roles with best practices and idempotent design patterns."
keywords: ["ansible", "playbook", "role", "inventory", "task", "handler", "vars"]
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

| Tool | Purpose | Auto-approved |
|------|---------|---------------|
| `lint_file` | Run ansible-lint on file or role directory | ✅ |
| `syntax_check` | Validate playbook syntax without execution | ✅ |
| `diff_check` | Preview changes with --check --diff mode | ❌ |
| `gather_facts` | Collect all facts from a host | ❌ |
| `list_hosts` | Show hosts affected by playbook | ✅ |
| `list_tags` | List all tags in playbook | ✅ |

All tools require `project_root` parameter (absolute path to Ansible workspace).

---

## Available Steering Files

Comprehensive guides for Ansible workflows and best practices:

- **ansible-best-practices.md** - Core patterns, idempotency, YAML style, naming conventions
- **ansible-role-structure.md** - Role directory layout, task organization, handlers, defaults
- **ansible-playbook-workflow.md** - Playbook creation, execution patterns, play structure
- **ansible-inventory.md** - Inventory structure, group_vars, host_vars, dynamic inventory
- **ansible-vault.md** - Secrets management with Ansible Vault, encryption patterns
- **ansible-collections.md** - Galaxy collections, requirements.yml, namespace management

Read specific guides with: `action="readSteering", steeringFile="<name>.md"`

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

### Creating ansible.cfg / inventory
1. Write the files directly using your file tools
2. Follow the structure in the steering file `ansible-inventory.md`
3. Verify inventory with `list_hosts` on any playbook
