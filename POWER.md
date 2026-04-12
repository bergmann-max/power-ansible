---
name: "ansible"
displayName: "Ansible Power"
author: "Max Bergmann"
description: "Build, lint, and validate Ansible playbooks and roles with best practices, proper structure, and idempotent design patterns."
keywords: ["ansible", "playbook", "role", "inventory", "task", "handler", "vars", "yaml", "automation", "infrastructure", "idempotent", "hosts", "galaxy", "collections"]
mcpServers: ["ansible"]
---

# Ansible Power – Onboarding & Steering

## Onboarding

### Step 1: Verify Ansible is installed
Before writing any Ansible content, confirm the toolchain is ready:
```bash
ansible --version
ansible-lint --version
```
If `ansible` is not found, inform the user and ask them to install Ansible and ansible-lint
via their preferred method (e.g. package manager, pip, or pipx).

### Step 2: Check the project structure
A proper Ansible project looks like this:
```
project/
├── ansible.cfg
├── inventory/
│   ├── hosts.ini          # or hosts.yml
│   └── group_vars/
│       └── all.yml
├── playbooks/
│   └── site.yml
└── roles/
    └── <role_name>/
        ├── tasks/main.yml
        ├── handlers/main.yml
        ├── defaults/main.yml
        ├── vars/main.yml
        ├── templates/
        ├── files/
        └── meta/main.yml
```
If no `ansible.cfg` exists, create one using the `create_ansible_cfg` MCP tool.

### Step 3: Install the lint-on-save hook
Add the following hook to `.kiro/hooks/ansible-lint-on-save.kiro.hook` in the workspace:

```json
{
  "name": "Ansible Lint on Save",
  "description": "Runs ansible-lint when a playbook or role task file is saved",
  "version": "1.0.0",
  "when": {
    "type": "fileEdited",
    "patterns": ["playbooks/**/*.yml", "roles/**/tasks/*.yml", "roles/**/handlers/*.yml"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "The file {{file}} was saved. Run `lint_file` via the ansible MCP tool on this file and show any lint errors with an explanation and suggested fix."
  }
}
```

### Step 4: Validate new files automatically
After creating or editing a playbook or role task file, always run:
```bash
ansible-lint <file>
ansible-playbook --syntax-check -i inventory/hosts.ini <playbook>
```
Use the `lint_file` and `syntax_check` MCP tools for this.

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

---
