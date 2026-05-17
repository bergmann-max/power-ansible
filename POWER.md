---
name: "ansible"
displayName: "Power Ansible"
description: "Build, lint, and validate Ansible playbooks and roles with best practices and idempotent design patterns."
keywords: ["ansible", "playbook", "handler", "role", "ansible-task", "ansible-lint", "ansible-inventory"]
author: "Max Bergmann"
---

# Ansible Power

## MCP Tools

| Tool | Purpose | Structured key | Auto-approved |
|------|---------|----------------|---------------|
| `lint_file` | Run ansible-lint on file or role directory | `findings[]` | true |
| `syntax_check` | Validate playbook syntax without execution | `errors[]` | true |
| `diff_check` | Preview changes with --check --diff mode | `recap{host}` | false |
| `gather_facts` | Collect all facts from a host | `facts{}` | false |
| `list_hosts` | Show hosts affected by playbook | `hosts[]` | true |
| `list_tags` | List all tags in playbook | `tags[]` | true |

Shape: `{ok, stdout, stderr, <structured key>}`. Structured key = parsed output; raw `stdout`/`stderr` for debug/parse fallback.

Workspace: auto via MCP `roots`. Else pass `project_root` as absolute path per call.

Inventory order:
1. `ANSIBLE_INVENTORY` env var
2. `ansible.cfg` → `[defaults] inventory`
3. Fallback: `hosts.yml`, `hosts.yaml`, `hosts.ini`, `inventory/hosts.*`

---

## When to Load Steering Files

- Code style, idempotency, YAML, naming → `ansible-best-practices.md`
- New role → `ansible-role-structure.md`
- Create/run playbooks → `ansible-playbook-workflow.md`
- Jinja2 templates, filters, lookups, `when:` → `ansible-jinja.md`
- Inventory, group_vars, host_vars → `ansible-inventory.md`
- Write/tune `ansible.cfg` → `ansible-config.md`
- Secrets, encrypted vars → `ansible-vault.md`
- Galaxy collections → `ansible-collections.md`

---

## Workflows

### Creating a new Playbook
1. Ask hosts/groups + tasks.
2. Write `playbooks/<name>.yml` via file tools.
3. Follow `ansible-playbook-workflow.md`.
4. `lint_file(path="/path/to/playbook.yml", project_root="/project/root")`
5. `syntax_check(playbook="/path/to/playbook.yml", project_root="/project/root")`

### Creating a new Role
1. Write role files via file tools:
   - `roles/<name>/tasks/main.yml`
   - `roles/<name>/handlers/main.yml`
   - `roles/<name>/defaults/main.yml`
   - `roles/<name>/vars/main.yml`
   - `roles/<name>/meta/main.yml`
   - `roles/<name>/README.md`
   - `roles/<name>/templates/` and `roles/<name>/files/` (empty dirs via `.gitkeep`)
2. Follow `ansible-role-structure.md`.
3. `lint_file(path="/path/to/roles/<name>", project_root="/project/root")`

### Updating an existing Playbook
1. `lint_file` first — record violations as baseline.
2. Edit via file tools. Preserve play skeleton from `ansible-best-practices.md`.
3. Re-run: `syntax_check` → `lint_file` (no new vs. baseline) → `diff_check` (see caveats).
4. Tasks added → `list_tags`.

### Refactoring a Playbook into a Role
1. One role = one concern. Split if playbook mixes install / configure / service.
2. Scaffold per `ansible-role-structure.md`.
3. Split tasks by concern → `tasks/install.yml`, `tasks/configure.yml`, `tasks/service.yml`. `tasks/main.yml` orchestrates via `include_tasks`.
4. Hard-coded values → `defaults/main.yml`, role-prefixed (`var-naming[no-role-prefix]`). Internal tables → `vars/main.yml`, `__` prefix.
5. Handlers → `handlers/main.yml` with `listen:`.
6. Replace source playbook with thin `roles:` caller.
7. Validate: `lint_file` on role dir, `syntax_check` on caller, `diff_check` on non-prod.
8. Run `diff_check` twice. Second run must report `changed=0`.

### Validating Playbook Design
1. Host targeting: `list_hosts(playbook="...", project_root="...")`. Optional `limit="webservers"` or `limit="web01.example.com"`.
2. Dry-run logic: `diff_check(playbook="...", project_root="...")`. Optional `limit="staging"`.

⚠ `diff_check` caveats — dry-run = *prediction*, not guarantee:
- Handlers no fire in check mode by default. Tasks depending on prior handler (e.g. service restart between tasks) report misleading diffs. Add `force_handlers: true` on play if handler order matters.
- `when: result.changed` chains skew results. Task gated on upstream `changed` reports skipped in check mode if upstream module lacks check-mode support — chain breaks silently. Prefer `notify` + handlers.
- `command` / `shell` / `script` skipped in check mode unless `check_mode: false` on task. Always report `skipping` — confirm idempotency otherwise.
- Modules without check-mode support (some 3rd-party collection modules) report no diff. Verify: `ansible-doc <fqcn> | grep "check_mode"`.
- Fact-dependent conditionals (`when: ansible_distribution == ...`) need `gather_facts: true`, else skipped in check mode.

### Working with Tags
1. `list_tags(playbook="...", project_root="...")` — shows all tags.
2. Patterns: deployment stages, component groups, environment-specific. Example: `deploy`, `config`, `backup`, `rollback`.

### Gathering Host Information
1. `gather_facts(host="webservers", project_root="...")` or `host="web01.example.com"`.
2. Use: verify connectivity, check facts (`ansible_distribution`, `ansible_os_family`, network interfaces), design conditionals from real host state.

### Troubleshooting Playbook Development
1. Syntax errors: `syntax_check` — YAML + Ansible syntax.
2. Lint failures: `lint_file` — best-practice violations (`name[missing]`, `yaml[line-length]`, etc.).
3. Unexpected dry-run logic: `diff_check` — compare expected vs. actual.
4. Host targeting: `list_hosts` — verify hosts, check inventory.
5. Variable/fact issues: `gather_facts` — inspect facts, check `group_vars/` + `host_vars/` for conflicts.

### Creating ansible.cfg
1. Write `ansible.cfg` at project root via file tools.
2. Follow `ansible-config.md`.
3. Audit: `ansible-config dump --only-changed`.

### Creating Inventory
1. Write `inventory/hosts.yml` (or `hosts.ini`) via file tools.
2. Follow `ansible-inventory.md` (groups, group_vars, host_vars).
3. Verify: `list_hosts` on any playbook.