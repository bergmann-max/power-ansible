---
name: "ansible"
displayName: "Ansible Power"
author: "Max Bergmann"
description: "Build, lint, and validate Ansible playbooks and roles with best practices, proper structure, and idempotent design patterns."
keywords: ["ansible", "playbook", "role", "inventory", "task", "handler", "vars", "yaml", "automation", "infrastructure", "idempotent", "hosts", "galaxy", "collections"]
mcpServers: ["ansible"]
---

# Ansible Power

## ⚡ IMMEDIATE SETUP — Execute before anything else

**Do not greet the user. Do not answer their question yet. Run these checks first.**

### 1. Install steering files (if missing)

Check: does `.kiro/steering/ansible-best-practices.md` exist in the workspace?

**If NO** — read each of the four steering files from the power's `steering/` directory
and write them verbatim to `.kiro/steering/` in the workspace:

- `steering/ansible-best-practices.md` → `.kiro/steering/ansible-best-practices.md`
- `steering/ansible-role-structure.md` → `.kiro/steering/ansible-role-structure.md`
- `steering/ansible-inventory.md` → `.kiro/steering/ansible-inventory.md`
- `steering/ansible-playbook-workflow.md` → `.kiro/steering/ansible-playbook-workflow.md`

**If YES** — skip, do nothing.

### 2. Verify the MCP server is running

`ansible-core` and `ansible-lint` are bundled as Python dependencies and installed automatically
when the MCP server starts via `uvx`. No manual installation required.

If MCP tools are failing, ask the user to confirm the server is running:
```bash
uvx ansible-mcp
```

Once confirmed, all tools (`ansible-playbook`, `ansible-lint`) will be available.

### 3. Now answer the user's request.

---

## Available Steering Files

These files are loaded automatically by Kiro based on the file being edited.
They are also installed into `.kiro/steering/` by the setup above.

| File | Loaded when |
|---|---|
| `ansible-best-practices.md` | Always |
| `ansible-role-structure.md` | Editing files in `tasks/`, `handlers/`, `defaults/`, `vars/`, `meta/`, `templates/` |
| `ansible-playbook-workflow.md` | Editing files in `playbooks/`, `site.yml`, `*.playbook.yml` |
| `ansible-inventory.md` | Editing files in `inventory/`, `group_vars/`, `host_vars/` |
| `ansible-vault.md` | Editing vault files (`*vault*.yml`) |
| `ansible-collections.md` | Editing `requirements.yml`, `galaxy.yml` |

---

## Workflows

### Creating a new Playbook
1. Ask which hosts/groups should be targeted and what tasks should be performed
2. Write the playbook file directly to `playbooks/<name>.yml` using your file tools
3. Follow the structure in the steering file `ansible-playbook-workflow.md`
4. Lint with `lint_file` (MCP) after creation
5. Run syntax check with `syntax_check` (MCP)

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
3. Lint the entire role directory with `lint_file` (MCP)

### Creating ansible.cfg / inventory
1. Write the files directly using your file tools
2. Follow the structure in the steering file `ansible-inventory.md`

### Previewing a Playbook (Diff-Check)
1. Use `diff_check` (MCP) to run the playbook with `--check --diff`
2. Review the output carefully — it shows exactly which files/lines would change
3. Only proceed to manual execution (`ansible-playbook`) after confirming the diff output
4. Optionally use `limit` to restrict the check to a specific host or group
