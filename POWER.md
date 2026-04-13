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

### 2. Install the lint-on-save hook (if missing)

Check: does `.kiro/hooks/ansible-lint-on-save.kiro.hook` exist in the workspace?

**If NO** — create it with this exact content:

```json
{
  "name": "Ansible Lint on Save",
  "description": "Runs ansible-lint when a playbook or role task file is saved",
  "version": "1.0.0",
  "when": {
    "type": "fileEdited",
    "patterns": ["playbooks/**/*.yml", "roles/**/tasks/*.yml", "roles/**/handlers/*.yml", "tasks/*.yml", "handlers/*.yml"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "The file {{file}} was saved. Run `lint_file` via the ansible MCP tool on this file and show any lint errors with an explanation and suggested fix."
  }
}
```

**If YES** — skip, do nothing.

### 3. Verify Ansible is installed

Run:
```bash
ansible --version
ansible-lint --version
```

If either command is not found, inform the user and ask them to install Ansible and ansible-lint
via their preferred method (e.g. package manager, pip, or pipx). Do not proceed until confirmed.

### 4. Now answer the user's request.

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

---

## Workflows

### Creating a new Playbook
1. Ask which hosts/groups should be targeted
2. Ask what tasks should be performed
3. Use `create_playbook` tool to scaffold the file
4. Always include `become: false` at play level unless root is explicitly needed
5. Lint with `lint_file` after creation
6. Run syntax check with `syntax_check`

### Creating a new Role
1. Use `create_role` tool to scaffold the full directory structure
2. Put logic into `tasks/main.yml` using `include_tasks` for complex roles
3. Define all variables with defaults in `defaults/main.yml`
4. Document the role purpose in `meta/main.yml`
5. Lint the entire role directory

### Previewing a Playbook (Diff-Check)
1. Use `diff_check` tool to run the playbook with `--check --diff`
2. Review the output carefully — it shows exactly which files/lines would change
3. Only proceed to manual execution (`ansible-playbook`) after confirming the diff output
4. Optionally use `limit` to restrict the check to a specific host or group
