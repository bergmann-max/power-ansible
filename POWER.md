---
name: "ansible"
displayName: "Ansible Automation"
description: "Build, lint, and run Ansible playbooks and roles with best practices, proper structure, and idempotent design patterns"
keywords: ["ansible", "playbook", "role", "inventory", "task", "handler", "vars", "yaml", "automation", "infrastructure", "idempotent", "hosts", "galaxy", "collections"]
mcpServers: ["ansible-dev"]
---

# Ansible Power – Onboarding & Steering

## Onboarding

### Step 1: Verify Ansible is installed
Before writing any Ansible content, confirm the toolchain is ready:
```bash
ansible --version
ansible-lint --version   # for linting
```
If `ansible` is not found, install it:
```bash
pip install ansible ansible-lint
```

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

### Step 3: Validate new files automatically
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

## Steering Rules

These rules apply to ALL Ansible content generated in this workspace:

- **Always use FQCN** (Fully Qualified Collection Name) for modules: `ansible.builtin.copy`, not `copy`
- **Always write idempotent tasks** – tasks must be safe to run multiple times
- **Never hardcode passwords** – use `ansible-vault` or environment variables
- **Use `notify` + handlers** for service restarts, never `ansible.builtin.service` in tasks directly after config changes
- **All variables** go in `defaults/main.yml` (low precedence, easy override) or `vars/main.yml` (high precedence, internal)
- **Templates** use Jinja2 with `.j2` extension in the `templates/` folder
- **Tags** should be added to every play and task for targeted execution
- **`when` conditions** use Ansible facts or registered variables, never shell commands inline
- **Loop items** use `loop:` not the deprecated `with_items:`
- **File permissions** are always explicit: `mode: '0644'`
