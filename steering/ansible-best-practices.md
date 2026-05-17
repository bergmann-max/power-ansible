# Ansible Best Practices – Project Conventions

Project rules + `ansible-lint` violations `lint_file` tool surface. General Ansible concepts:
<https://docs.ansible.com/ansible/latest/>.

## Hard rules in this project

1. **FQCN only** — every module call use `ansible.builtin.<name>` (or
   `<collection>.<name>` non-builtin). Lint: `fqcn[action]`.
2. **Mode is ugo, never octal** — `mode: 'u=rw,g=r,o=r'`, not `'0644'`. `o=`
   mandatory even when other no perms (`mode: 'u=rw,g=r,o='`).
3. **Pin versions** — `state: present` + pinned version, never
   `state: latest`. Lint: `package-latest`.
4. **Every task has a name** — uppercase first char. Lint:
   `name[missing]`, `name[casing]`.
5. **`command`/`shell` must use `cmd:` key** — no free-form args. Lint:
   `no-free-form`. Always set `changed_when:` (`false` for read-only).
   Lint: `no-changed-when`.
6. **No implicit type coercion** — use Jinja filters (e.g. `to_json`) when
   passing dicts/lists. Lint: `avoid-implicit`.
7. **Tags everywhere** — every task gets one+ tag for `--tags` filter.
8. **Truthy literals** — `true`/`false` only, never `yes/no/True/False`.
   Lint: `yaml[truthy]`.
9. **Role variable naming** — role vars prefixed with role name.
   Lint: `var-naming[no-role-prefix]`.

## Play skeleton

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: true
  tags: [webservers]

  vars:
    nginx_port: 80
    app_user: webapp

  tasks:
    - name: Install nginx
      ansible.builtin.package:
        name: nginx-1.24.0
        state: present
      tags: [packages]
      notify: Restart nginx

    - name: Copy nginx configuration
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: 'u=rw,g=r,o=r'
      tags: [config]
      notify: Restart nginx

  handlers:
    - name: Restart nginx         # uppercase, matches notify string exactly
      ansible.builtin.service:
        name: nginx
        state: restarted
```

## Idempotency — the critical rule

Every task must produce same outcome 2nd run as 1st. Use module state
semantics (`state: present/absent`) or `creates:`/`removes:` on
`command`/`shell`.

```yaml
# GOOD Idempotent — package module
- ansible.builtin.package: { name: nginx, state: present }

# GOOD Idempotent — creates: marker
- ansible.builtin.command:
    cmd: wget https://example.com/app.tar.gz -O /opt/app.tar.gz
    creates: /opt/app.tar.gz

# BAD Not idempotent — re-downloads every run
- ansible.builtin.command:
    cmd: wget https://example.com/app.tar.gz

# BAD Not idempotent — keeps appending
- ansible.builtin.shell: echo "config=value" >> /etc/app.conf
```

## Variable precedence — condensed (lowest → highest)

Condensed view of 14 most-used sources. Full Ansible spec lists ~22 levels
(command-line role params, connection vars, etc.) — see
<https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence>.
Top weakest, bottom always wins.

1. role defaults (`roles/*/defaults/main.yml`)
2. inventory file/script group vars
3. inventory `group_vars/all`
4. playbook `group_vars/all`
5. inventory `group_vars/*`
6. playbook `group_vars/*`
7. inventory `host_vars/*`
8. playbook `host_vars/*`
9. host facts / cached `set_facts`
10. play vars / `vars_prompt` / `vars_files`
11. role vars (`roles/*/vars/main.yml`)
12. block vars / task vars
13. `include_vars` / `set_facts` / registered vars
14. extra vars (`-e`) — always win

## Error handling

```yaml
# Custom failure condition
- name: Run command
  ansible.builtin.command: { cmd: /usr/bin/mycommand }
  register: result
  failed_when: "'ERROR' in result.stderr"

# Read-only command — never marks changed
- name: Check configuration
  ansible.builtin.command: { cmd: /usr/bin/check_config }
  register: config_check
  changed_when: false

# block / rescue / always
- name: Risky workflow
  block:
    - name: Risky task
      ansible.builtin.command: { cmd: /usr/bin/risky_operation }
  rescue:
    - name: Handle failure
      ansible.builtin.debug: { msg: "Operation failed, running recovery" }
  always:
    - name: Cleanup
      ansible.builtin.debug: { msg: "Cleanup complete" }
```

## Lint anti-patterns

### `no-handler` — use `notify`, not `when: result.changed`

```yaml
# BAD
- ansible.builtin.copy: { src: nginx.conf, dest: /etc/nginx/nginx.conf, mode: 'u=rw,g=r,o=r' }
  register: result
- ansible.builtin.service: { name: nginx, state: restarted }
  when: result.changed

# GOOD
- ansible.builtin.copy: { src: nginx.conf, dest: /etc/nginx/nginx.conf, mode: 'u=rw,g=r,o=r' }
  notify: Restart nginx
```

### `partial-become` — `become_user` requires `become: true` at the same level

```yaml
# GOOD
- ansible.builtin.service: { name: myapp, state: started }
  become: true
  become_user: appuser
```

### `risky-shell-pipe` — `set -o pipefail` when piping in `shell:`

```yaml
- ansible.builtin.shell:
    cmd: |
      set -o pipefail
      cat /etc/hosts | grep localhost
    executable: /bin/bash
  changed_when: false
```

### `no-log-password` — `no_log: true` when looping over secrets

```yaml
- ansible.builtin.user:
    name: "{{ item.name }}"
    password: "{{ item.password }}"
  loop: "{{ users }}"
  no_log: true
```

### `avoid-implicit` — explicit Jinja for non-string values

```yaml
# BAD
- ansible.builtin.copy:
    content: { "key": "value" }
    dest: /tmp/config.json

# GOOD
- vars: { config: { "key": "value" } }
  ansible.builtin.copy:
    content: "{{ config | to_json }}"
    dest: /tmp/config.json
```

### `import-task-no-when` — `when:` on `import_tasks` is evaluated once

Use `include_tasks` when condition depends on runtime state.

### `when:` may only reference facts / registered vars

```yaml
# GOOD
- ansible.builtin.package: { name: nginx, state: present }
  when: ansible_os_family == "Debian"

# GOOD
- ansible.builtin.service: { name: nginx, state: restarted }
  when: config_result.changed

# BAD shell-command-in-when — fragile and not declarative
- ansible.builtin.debug: { msg: "exists" }
  when: "{{ lookup('pipe', 'test -f /etc/nginx/nginx.conf') }}"
```

## Loops

Use `loop:`, never `with_items:`. Always set `loop_control.label` so progress
output stays readable.

```yaml
- name: Create users
  ansible.builtin.user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
    state: present
  loop:
    - { name: alice, groups: admin,developers }
    - { name: bob,   groups: developers }
  loop_control:
    label: "{{ item.name }}"
```

In roles, prefix loop variable to avoid collisions with outer loops
(see `ansible-role-structure.md`).

## Module choice cheatsheet

| Need | Use | Notes |
|---|---|---|
| Static file | `ansible.builtin.copy` | `backup: true` for safety |
| Dynamic content | `ansible.builtin.template` | `validate:` for config files |
| Single line edit | `ansible.builtin.lineinfile` | |
| Multi-line block | `ansible.builtin.blockinfile` | set `marker:` |
| Cross-platform pkg | `ansible.builtin.package` | |
| Cross-platform svc | `ansible.builtin.service` | |
| Systemd-only | `ansible.builtin.systemd` | `daemon_reload: true` after unit changes |
| Simple command | `ansible.builtin.command` | always `cmd:` + `changed_when:` |
| Pipes/redirects | `ansible.builtin.shell` | `set -o pipefail` |
| Run local script remotely | `ansible.builtin.script` | use `creates:` |
| No Python on target | `ansible.builtin.raw` | only for bootstrap |

## Tag strategy

Tags drive `--tags` / `--skip-tags`. Two special tags:

- `always` — runs regardless of `--tags` filter.
- `never` — runs only when explicitly listed in `--tags`.

```yaml
tasks:
  - name: Pre-flight assertions
    ansible.builtin.assert: { that: ["app_user is defined"] }
    tags: [always]

  - name: Install packages
    ansible.builtin.package: { name: nginx, state: present }
    tags: [packages, nginx]

  - name: Destructive test
    ansible.builtin.command: { cmd: /usr/local/bin/test_nginx.sh }
    changed_when: false
    tags: [never, testing]   # only on --tags testing
```

## Async tasks (long-running operations)

```yaml
- name: Long running operation
  ansible.builtin.command: { cmd: /usr/bin/long_process }
  async: 3600
  poll: 0
  register: long_task

- name: Wait for completion
  ansible.builtin.async_status:
    jid: "{{ long_task.ansible_job_id }}"
  register: job_result
  until: job_result.finished
  retries: 30
  delay: 10
```

## Privilege escalation

```yaml
# Play-wide
- hosts: all
  become: true
  become_method: sudo

# Per-task — both keys at the same level
- name: Start as app user
  ansible.builtin.service: { name: myapp, state: started }
  become: true
  become_user: appuser
```

## Performance

```ini
# ansible.cfg
[defaults]
forks = 20
pipelining = True

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

```yaml
# Skip facts when not needed
- hosts: all
  gather_facts: false

# Or gather only what you need
- hosts: all
  gather_facts: true
  gather_subset:
    - "!all"
    - network
```

## Secrets

Never plain text in repo. Use one of:

- `ansible-vault` encrypted strings (see `ansible-vault.md`)
- `lookup('env', 'VAR')`
- `lookup('hashi_vault', 'secret=...')`

## `.ansible-lint` baseline

Tested against `ansible-lint 26.x` / `ansible-core 2.20.x`.

```yaml
profile: production
offline: true
enable_list:
  - no-log-password           # opt-in: requires no_log on secret loops
  - loop-var-prefix           # opt-in: enforces loop_var_prefix below
loop_var_prefix: "^(__|{role}_)"   # {role} is substituted at runtime by ansible-lint
var_naming_pattern: "^[a-z_][a-z0-9_]*$"
```

Notes:

- `args` already on in `production` profile — do not list in `enable_list`.
  Violations surface sub-error labels: `args[module]` (module argspec
  mismatch), `args[python]` (Python module load error).
- Per-file suppressions go in `.ansible-lint-ignore`, not `skip_list`.
- Power repo does **not** ship `.ansible-lint`. Copy baseline block
  above into consuming project's root on first onboarding.

## ansible-lint rules — quick reference

| Rule | Profile | What it checks |
|---|---|---|
| `name[missing]` | basic | every task must have `name:` |
| `name[casing]` | moderate | task names must start uppercase |
| `no-changed-when` | shared | `command`/`shell` must set `changed_when:` |
| `no-free-form` | basic | no inline args on `command`/`shell` — use `cmd:` |
| `fqcn[action]` | production | always use FQCN |
| `var-naming[no-role-prefix]` | basic | role vars must start with role name |
| `yaml[truthy]` | basic | `true`/`false` only |
| `key-order` | basic | `name` first; `block`/`rescue`/`always` last |
| `no-handler` | shared | use `notify`+handler instead of `when: result.changed` |
| `partial-become` | basic | `become_user` needs `become: true` at same level |
| `package-latest` | safety | never `state: latest` |
| `risky-shell-pipe` | safety | `set -o pipefail` when piping in `shell` |
| `risky-file-permissions` | safety | always set `mode:` explicitly |
| `avoid-implicit` | safety | no implicit type coercion |
| `ignore-errors` | shared | never `ignore_errors: true` without comment |
| `no-log-password` | opt-in | `no_log: true` when looping over secrets |
| `loop-var-prefix` | opt-in | role loop vars must use prefix |
| `import-task-no-when` | production | `when:` on `import_tasks` evaluates once — use `include_tasks` |
| `single-entry-point` | production | role must have single `tasks/main.yml` |

## Validation workflow

MCP tools enforce in order:

1. `syntax_check` — fast structural check
2. `lint_file` — production-profile rules (see above)
3. `diff_check` — dry-run with `--check --diff`

Docs: <https://docs.ansible.com/projects/lint/rules/>
