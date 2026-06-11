---
name: "ansible"
displayName: "Ansible"
description: "Build, lint, and validate Ansible playbooks and roles with best practices and idempotent design patterns."
keywords: ["ansible", "playbook", "role", "handler", "inventory", "vault"]
author: "Max Bergmann"
---

# Ansible

## Overview

MCP server + steering files for authoring Ansible playbooks and roles. Tools wrap `ansible-lint`, `ansible-playbook --syntax-check`, `--check --diff`, fact gathering, host/tag listing. Steering files codify production-profile lint rules, FQCN, idempotency, role layout, Jinja2, vault, Galaxy collections.
## Onboarding

**Execute these steps immediately and silently when this power is activated. Do not summarize or ask for confirmation — just do it.**

### Step 1: Check uv

Run `uv --version` in the terminal. If the command fails, tell the user:

> `uv` is required for the MCP server. Install it:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
> Then re-activate this power.

If `uv` is present, continue to Step 2 without any output.

### Step 2: Install slash command hooks

Check if `.kiro/hooks/ansible-new-playbook.kiro.hook` exists in the workspace root. If any of the three files below are missing, create them now. Do not overwrite files that already exist.

`.kiro/hooks/ansible-new-playbook.kiro.hook`:
```json
{
  "enabled": true,
  "name": "ansible-new-playbook",
  "description": "Scaffold a new Ansible playbook following the project conventions",
  "version": "1",
  "when": {
    "type": "userTriggered"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Scaffold a new Ansible playbook:\n1. Ask user for the playbook name\n2. Load the steering file 'ansible-playbook-workflow.md' from this power\n3. Create playbooks/<name>.yml following the required structure skeleton (hosts, gather_facts, become, tags, pre_tasks, tasks, handlers, post_tasks)\n4. Use the skeleton from the steering file - include assert in pre_tasks, proper tag structure\n5. Run syntax_check on the created playbook\n6. Run lint_file with profile='production' on the created playbook"
  }
}
```

`.kiro/hooks/ansible-new-role.kiro.hook`:
```json
{
  "enabled": true,
  "name": "ansible-new-role",
  "description": "Scaffold a new Ansible role following the project conventions",
  "version": "1",
  "when": {
    "type": "userTriggered"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Scaffold a new Ansible role:\n1. Ask user for the role name\n2. Load the steering file 'ansible-role-structure.md' from this power\n3. Create the complete directory structure: roles/<name>/tasks/main.yml, handlers/main.yml, defaults/main.yml, vars/main.yml, meta/main.yml, README.md, templates/.gitkeep, files/.gitkeep\n4. Follow the skeleton patterns from the steering file for each file\n5. Populate tasks/main.yml with the include_tasks orchestration skeleton\n6. Populate defaults/main.yml with commented vars\n7. Populate meta/main.yml with galaxy_info stub\n8. Run lint_file on the created role directory"
  }
}
```

`.kiro/hooks/ansible-fix-lint.kiro.hook`:
```json
{
  "enabled": true,
  "name": "ansible-fix-lint",
  "description": "Auto-fix mechanically fixable ansible-lint violations",
  "version": "1",
  "when": {
    "type": "userTriggered"
  },
  "then": {
    "type": "askAgent",
    "prompt": "Auto-fix ansible-lint violations on the current file/role:\n1. Identify the target file or role directory (ask user if ambiguous)\n2. Load steering file 'ansible-best-practices.md' from this power\n3. Run lint_file with profile='production' on the target\n4. For each fixable finding, apply the fix per the steering rules:\n   - name[missing]: add name to unnamed task\n   - name[casing]: uppercase first letter\n   - fqcn[action]: add ansible.builtin. prefix\n   - yaml[truthy]: yes/no → true/false\n   - no-free-form: wrap in cmd: key\n   - no-changed-when: add changed_when: false for read-only commands\n   - package-latest: pin version, change state to present\n5. Show a table: fixed violations vs remaining (non-mechanical)\n6. Re-run lint_file to confirm which are resolved"
  }
}
```

After writing the hook files, confirm once with a single line:
> Ansible slash commands installed: `/ansible-new-playbook`, `/ansible-new-role`, `/ansible-fix-lint`

**Note:** MCP server first start takes ~30s — `uvx` downloads and caches `ansible-core`, `ansible-lint`, `mcp`. Subsequent starts are instant.

## MCP Tools

| Tool | Purpose | Inventory | Structured key | Timeout |
|------|---------|-----------|----------------|---------|
| `lint_file` | ansible-lint on file or role dir | no | `findings[]` | 300s |
| `syntax_check` | Validate playbook syntax | no | `errors[]` | 60s |
| `diff_check` | `--check --diff` dry-run | yes | `recap{host}` | 300s |
| `gather_facts` | Run setup module on host/group | yes | `facts{host}` | 300s |
| `list_hosts` | Hosts affected by playbook | yes | `hosts[]` | 60s |
| `list_tags` | Tags defined in playbook | yes | `tags[]` | 60s |

**Return shape (all tools):** `{ok: bool, stdout: str, stderr: str, <structured key>}`. On validation failure (missing path, bad `project_root`, no inventory): `{ok: false, error: str}` - no `stdout`/`stderr`.

**Workspace resolution:** MCP `roots` capability first; else `project_root` (absolute path) required per call. Relative paths or unresolved `${VAR}` rejected.

**Inventory resolution** (`diff_check`, `gather_facts`, `list_hosts`, `list_tags`):

1. `ANSIBLE_INVENTORY` env var (passed verbatim - supports comma-lists)
2. `ansible.cfg` → `[defaults] inventory` (comma-list resolved vs `project_root`)
3. Fallback: `hosts.yml`, `hosts.yaml`, `hosts.ini`, `inventory/hosts.*`

### `lint_file`

```text
lint_file(path: str, project_root: str = "", profile: str = "production")
```

| Arg | Type | Required | Default | Notes |
|-----|------|----------|---------|-------|
| `path` | str | yes | - | Absolute, or relative to `project_root`. File or role dir. |
| `project_root` | str | conditional | `""` | Required when MCP `roots` unavailable. Absolute. |
| `profile` | str | no | `"production"` | `min` \| `basic` \| `moderate` \| `safety` \| `shared` \| `production` \| `default` (= use repo `.ansible-lint`). |

Returns `findings: [{rule, severity, file, line, message, url}]` parsed from `ansible-lint --format json`. Empty list on clean lint.

### `syntax_check`

```text
syntax_check(playbook: str, project_root: str = "")
```

| Arg | Type | Required | Default | Notes |
|-----|------|----------|---------|-------|
| `playbook` | str | yes | - | Path to playbook file. |
| `project_root` | str | conditional | `""` | See workspace resolution. |

Returns `errors: [str]` - non-`[WARNING]` stderr lines when `ok=false`. Empty list when syntax valid.

### `diff_check`

```text
diff_check(playbook: str, project_root: str = "", limit: str = "")
```

| Arg | Type | Required | Default | Notes |
|-----|------|----------|---------|-------|
| `playbook` | str | yes | - | Path to playbook file. |
| `project_root` | str | conditional | `""` | See workspace resolution. |
| `limit` | str | no | `""` | `--limit` pattern: group, host, or comma-list. |

Returns `recap: {host: {ok, changed, unreachable, failed, skipped, rescued, ignored}}` parsed from PLAY RECAP. Diff bodies in raw `stdout`. **Connects to real hosts via SSH** - gated, never auto-approve. Dry-run caveats: see `## Troubleshooting → diff_check misleading output`.

### `gather_facts`

```text
gather_facts(host: str, project_root: str = "")
```

| Arg | Type | Required | Default | Notes |
|-----|------|----------|---------|-------|
| `host` | str | yes | - | Inventory hostname OR group name. |
| `project_root` | str | conditional | `""` | See workspace resolution. |

Returns `facts: {hostname: {ansible_facts}}` for `SUCCESS` hosts only. `UNREACHABLE!` / `FAILED!` hosts silently dropped - check raw `stdout` to detect. Single-host call = one-entry map.

### `list_hosts`

```text
list_hosts(playbook: str, project_root: str = "", limit: str = "")
```

| Arg | Type | Required | Default | Notes |
|-----|------|----------|---------|-------|
| `playbook` | str | yes | - | Path to playbook file. |
| `project_root` | str | conditional | `""` | See workspace resolution. |
| `limit` | str | no | `""` | `--limit` pattern. |

Returns `hosts: [str]` - flat list parsed from `ansible-playbook --list-hosts`.

### `list_tags`

```text
list_tags(playbook: str, project_root: str = "")
```

| Arg | Type | Required | Default | Notes |
|-----|------|----------|---------|-------|
| `playbook` | str | yes | - | Path to playbook file. |
| `project_root` | str | conditional | `""` | See workspace resolution. |

Returns `tags: [str]` - deduplicated, sorted, parsed from `TASK TAGS: [...]` lines.

---

## Tool Usage Examples

### Lint a Playbook or Role

```text
lint_file(path="playbooks/site.yml", project_root="/home/user/ansible-repo")
// Returns { findings: [] } on clean pass
// Returns { findings: [{rule, severity, file, line, message, url}] } on violations

lint_file(path="roles/nginx", project_root="/home/user/ansible-repo", profile="production")
// Role-level rules fire only on full directory - don't lint isolated tasks/main.yml
```

### Validate Syntax

```text
syntax_check(playbook="playbooks/site.yml", project_root="/home/user/ansible-repo")
// Returns { ok: true, errors: [] }
// On failure: { ok: false, errors: ["ERROR! ...", ...] }
```

### Dry-Run Against Real Hosts

```text
diff_check(playbook="playbooks/site.yml", project_root="/home/user/ansible-repo", limit="staging")
// Returns { recap: {host: {ok, changed, unreachable, failed, skipped, rescued, ignored}} }
// ⚠ Needs SSH to real hosts - gate behind user approval
```

### Inspect Before Editing (Read-Only)

```text
// What hosts does this playbook target?
list_hosts(playbook="playbooks/site.yml", project_root="/home/user/ansible-repo")
// Returns { hosts: ["web01.example.com", "web02.example.com"] }

// What tags can I filter by?
list_tags(playbook="playbooks/site.yml", project_root="/home/user/ansible-repo")
// Returns { tags: ["always", "config", "install", "never", "packages"] }

// What facts does a host expose?
gather_facts(host="web01.example.com", project_root="/home/user/ansible-repo")
// Returns { facts: {web01.example.com: {ansible_distribution: "Ubuntu", ...}} }
```

### Full Validation Chain

```text
// 1. Syntax first (no inventory, no SSH)
syntax_check(playbook="playbooks/web.yml", project_root="/home/user/ansible-repo")
// → { ok: true, errors: [] }

// 2. Lint with production profile
lint_file(path="playbooks/web.yml", project_root="/home/user/ansible-repo", profile="production")
// → { findings: [{rule: "name[missing]", severity: "VERY_HIGH", file: "playbooks/web.yml", line: 12}] }

// 3. Dry-run against staging (SSH required)
diff_check(playbook="playbooks/web.yml", project_root="/home/user/ansible-repo", limit="staging")
// → { recap: {web01: {ok: 3, changed: 1, unreachable: 0, failed: 0, skipped: 0}} }
```

---

## Available Steering Files

Load on demand per task - do not preload all.

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

1. `lint_file` first - record violations as baseline.
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

⚠ `diff_check` caveats - dry-run = *prediction*, not guarantee:

- Handlers no fire in check mode by default. Tasks depending on prior handler (e.g. service restart between tasks) report misleading diffs. Add `force_handlers: true` on play if handler order matters.
- `when: result.changed` chains skew results. Task gated on upstream `changed` reports skipped in check mode if upstream module lacks check-mode support - chain breaks silently. Prefer `notify` + handlers.
- `command` / `shell` / `script` skipped in check mode unless `check_mode: false` on task. Always report `skipping` - confirm idempotency otherwise.
- Modules without check-mode support (some 3rd-party collection modules) report no diff. Verify: `ansible-doc <fqcn> | grep "check_mode"`.
- Fact-dependent conditionals (`when: ansible_distribution == ...`) need `gather_facts: true`, else skipped in check mode.

### Working with Tags

1. `list_tags(playbook="...", project_root="...")` - shows all tags.
2. Patterns: deployment stages, component groups, environment-specific. Example: `deploy`, `config`, `backup`, `rollback`.

### Gathering Host Information

1. `gather_facts(host="webservers", project_root="...")` or `host="web01.example.com"`.
2. Use: verify connectivity, check facts (`ansible_distribution`, `ansible_os_family`, network interfaces), design conditionals from real host state.

### Troubleshooting Playbook Development

1. Syntax errors: `syntax_check` - YAML + Ansible syntax.
2. Lint failures: `lint_file` - best-practice violations (`name[missing]`, `yaml[line-length]`, etc.).
3. Unexpected dry-run logic: `diff_check` - compare expected vs. actual.
4. Host targeting: `list_hosts` - verify hosts, check inventory.
5. Variable/fact issues: `gather_facts` - inspect facts, check `group_vars/` + `host_vars/` for conflicts.

### Creating ansible.cfg

1. Write `ansible.cfg` at project root via file tools.
2. Follow `ansible-config.md`.
3. Audit: `ansible-config dump --only-changed`.

### Creating Inventory

1. Write `inventory/hosts.yml` (or `hosts.ini`) via file tools.
2. Follow `ansible-inventory.md` (groups, group_vars, host_vars).
3. Verify: `list_hosts` on any playbook.

---

## Troubleshooting

Power-specific failure modes. Ansible-level troubleshooting → "Troubleshooting Playbook Development" workflow above.

### MCP server fails to start

- **`uvx: command not found`** - `uv` missing. Install per `## Onboarding` above.
- **First start hangs ~30s** - `uvx` resolves `ansible-core`, `ansible-lint`, `mcp` on first call. Subsequent starts cached.
- **`git+https://...@0.3.0` not found** - `mcp-ansible` repo unreachable or tag removed. Check network + `https://github.com/bergmann-max/mcp-ansible/tags`.
- **Server starts, tools not visible** - Reload Kiro Powers Panel. Inspect MCP logs for handshake errors.

### `project_root` resolution

- **`roots not provided` / tool errors out** - Kiro did not pass workspace `roots` via MCP protocol. Pass explicit `project_root="/absolute/path"` on every call.
- **Relative path** - Always fails. Must be absolute.
- **Wrong path** - Silent: `lint_file` finds no files, `list_hosts` returns empty. Verify path matches repo root containing `ansible.cfg` / `inventory/`.

### Inventory not found

`list_hosts` empty or `gather_facts` fails on group name → inventory resolution failed. Resolution order:

1. `ANSIBLE_INVENTORY` env var - **scope = MCP server process**, not your shell. Set via Kiro MCP env config, not `.bashrc`.
2. `ansible.cfg` → `[defaults] inventory = ...`
3. Fallback: `hosts.yml`, `hosts.yaml`, `hosts.ini`, `inventory/hosts.*` relative to `project_root`.

### Lint vs. syntax divergence

- `lint_file` clean, playbook still fails at runtime → `lint_file` does not catch all syntax edges. Always run `syntax_check` in addition.
- `lint_file` on a role directory vs. a single task file produces different rule sets (role-level rules only fire on full role tree). Lint the whole `roles/<name>/` dir, not isolated task files.

### `diff_check` misleading output

Dry-run = prediction, not guarantee. Full caveat list in "Validating Playbook Design" workflow above. Common cases:

- Handlers do not fire in check mode → add `force_handlers: true` if downstream tasks depend on handler side effects.
- `command`/`shell`/`script` skipped unless `check_mode: false` per task.
- 3rd-party modules without check-mode support report no diff. Verify via `ansible-doc <fqcn> | grep check_mode`.

### Vault errors during `lint_file` / `syntax_check`

- **`no vault secrets found`** - `vault_password_file` not configured. Set in `ansible.cfg` or via `ANSIBLE_VAULT_PASSWORD_FILE` env in MCP server process. See `ansible-vault.md`.
- **`Decryption failed`** - wrong password or missing `--vault-id` when multiple IDs in use.

### `diff_check` requires SSH to real hosts

Unlike `lint_file` / `syntax_check` (offline), `diff_check` connects to inventory hosts via SSH. Failure modes:

- No SSH key / wrong user → connection timeout.
- `host_key_checking = True` + unknown host → first run fails. Provision `known_hosts` or set `False` in `ansible.cfg`.
- Always run against staging/limit first: `limit="staging"`.

---

## Resources

- [Ansible Documentation](https://docs.ansible.com/ansible/latest/)
- [ansible-lint Rules](https://docs.ansible.com/projects/lint/rules/)
- [Ansible Galaxy](https://galaxy.ansible.com)
- [Jinja2 Template Designer](https://jinja.palletsprojects.com/en/stable/templates/)
- [MCP Server (mcp-ansible)](https://github.com/bergmann-max/mcp-ansible)
- [Kiro Powers Docs](https://kiro.dev/docs/powers/)
- [Install `uv`](https://docs.astral.sh/uv/)
