---
inclusion: always
---

# Ansible Development – Best Practices & Reference

## Overview
This steering file provides best practices for infrastructure as code, proper YAML formatting, idempotent task design, and effective use of Ansible's features.

## Core Concepts

### Directory Structure
Standard Ansible project layout:
```
ansible-project/
├── ansible.cfg
├── inventory/
│   ├── production/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── staging/
│       ├── hosts.yml
│       └── group_vars/
├── playbooks/
│   ├── site.yml
│   ├── webservers.yml
│   └── databases.yml
├── roles/
│   ├── common/
│   │   ├── tasks/
│   │   ├── handlers/
│   │   ├── templates/
│   │   ├── files/
│   │   ├── vars/
│   │   ├── defaults/
│   │   └── meta/
│   └── nginx/
└── group_vars/
    ├── all.yml
    └── webservers.yml
```

## Best Practices

### 1. Idempotency
**Critical Rule:** Every task should be idempotent - running it multiple times should produce the same result without unintended side effects.

```yaml
# ✅ Idempotent - uses ansible.builtin.package
- name: Ensure nginx is installed
  ansible.builtin.package:
    name: nginx
    state: present

# ✅ Idempotent - uses creates parameter
- name: Download application
  ansible.builtin.command:
    cmd: wget https://example.com/app.tar.gz
    creates: /opt/app.tar.gz

# ❌ Not idempotent - always executes
- name: Download application
  ansible.builtin.command:
    cmd: wget https://example.com/app.tar.gz

# ❌ Not idempotent - always appends
- name: Add line to file
  ansible.builtin.shell: echo "config=value" >> /etc/app.conf
```

### 2. YAML Formatting
```yaml
---
- name: Configure web servers
  hosts: webservers
  become: true

  vars:
    nginx_port: 80
    app_user: webapp

  tasks:
    - name: Install nginx
      ansible.builtin.package:
        name: nginx
        state: present
      notify: Restart nginx

    - name: Copy nginx configuration
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: 'u=rw,g=r,o=r'
      notify: Restart nginx

  handlers:
    - name: Restart nginx         # uppercase, matches notify string exactly
      ansible.builtin.service:
        name: nginx
        state: restarted
```

### 3. Module Usage – Always use FQCN
```yaml
# ✅ Good - FQCN format (required)
- name: Create directory
  ansible.builtin.file:
    path: /opt/app
    state: directory
    mode: 'u=rwx,g=rx,o=rx'

# ⚠️ Acceptable but not recommended
- name: Create directory
  file:
    path: /opt/app
    state: directory
```

### 4. Variable Precedence (lowest → highest)
1. role defaults
2. inventory file/script group vars
3. inventory group_vars/all
4. playbook group_vars/all
5. inventory group_vars/*
6. playbook group_vars/*
7. inventory host_vars/*
8. playbook host_vars/*
9. host facts / cached set_facts
10. play vars / vars_prompt / vars_files
11. role vars
12. block vars / task vars
13. include_vars / set_facts / registered vars
14. extra vars (always win)

### 5. Error Handling
```yaml
# Use failed_when for custom failure conditions
- name: Run command
  ansible.builtin.command:
    cmd: /usr/bin/mycommand
  register: result
  failed_when: "'ERROR' in result.stderr"

# Use changed_when to control change status
- name: Check configuration
  ansible.builtin.command:
    cmd: /usr/bin/check_config
  register: config_check
  changed_when: false

# Use blocks for error handling
- name: Handle errors with blocks
  block:
    - name: Risky task
      ansible.builtin.command:
        cmd: /usr/bin/risky_operation
  rescue:
    - name: Handle failure
      ansible.builtin.debug:
        msg: "Operation failed, running recovery"
  always:
    - name: Always runs
      ansible.builtin.debug:
        msg: "Cleanup complete"
```

## Common Patterns

### no-handler – use `notify` instead of `when: result.changed`
```yaml
# ❌ no-handler violation – acts as a handler but isn't one
- name: Copy config
  ansible.builtin.copy:
    src: nginx.conf
    dest: /etc/nginx/nginx.conf
    mode: 'u=rw,g=r,o=r'
  register: result

- name: Restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted
  when: result.changed   # <- no-handler violation

# ✅ Correct – use notify + handler
- name: Copy config
  ansible.builtin.copy:
    src: nginx.conf
    dest: /etc/nginx/nginx.conf
    mode: 'u=rw,g=r,o=r'
  notify: Restart nginx
```

### no-log-password – protect secrets in loops (opt-in rule)
```yaml
# ❌ Passwords in loops get logged
- name: Create users
  ansible.builtin.user:
    name: "{{ item.name }}"
    password: "{{ item.password }}"
  loop: "{{ users }}"

# ✅ Always set no_log: true when looping over sensitive data
- name: Create users
  ansible.builtin.user:
    name: "{{ item.name }}"
    password: "{{ item.password }}"
  loop: "{{ users }}"
  no_log: true
```

### avoid-implicit – always use explicit Jinja2 for non-string values
```yaml
# ❌ avoid-implicit violation – dict passed directly to copy.content
- name: Write config file
  ansible.builtin.copy:
    content: { "key": "value" }
    dest: /tmp/config.json

# ✅ Explicit Jinja2 filter
- name: Write config file
  vars:
    config: { "key": "value" }
  ansible.builtin.copy:
    content: "{{ config | to_json }}"
    dest: /tmp/config.json
```

### Conditional Execution
```yaml
- name: Install package on RedHat family
  ansible.builtin.dnf:
    name: httpd
    state: present
  when: ansible_os_family == "RedHat"

# Multiple conditions
- name: Complex conditional
  ansible.builtin.debug:
    msg: "This runs on Ubuntu 20.04+"
  when:
    - ansible_distribution == "Ubuntu"
    - ansible_distribution_version is version('20.04', '>=')
```

### Loops – use `loop:` not `with_items:`
```yaml
# ✅ Modern loop
- name: Install multiple packages
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - postgresql
    - redis

# Loop with dictionary
- name: Create multiple users
  ansible.builtin.user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
    state: present
  loop:
    - { name: 'alice', groups: 'admin,developers' }
    - { name: 'bob', groups: 'developers' }
  loop_control:
    label: "{{ item.name }}"
```

### Jinja2 Templates
```jinja2
{# templates/nginx.conf.j2 #}
{# Managed by Ansible – manual changes will be overwritten! #}
user {{ nginx_user }};
worker_processes {{ ansible_processor_vcpus }};

{% if nginx_ssl_enabled %}
ssl_protocols TLSv1.2 TLSv1.3;
ssl_certificate {{ nginx_ssl_cert }};
{% endif %}

upstream backend {
{% for host in groups['backend_servers'] %}
    server {{ hostvars[host]['ansible_default_ipv4']['address'] }}:8080;
{% endfor %}
}
```

## Secrets – Never in Plain Text
```yaml
# ❌ Never
db_password: "supersecret123"

# ✅ With ansible-vault
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...

# ✅ From environment variable
db_password: "{{ lookup('env', 'DB_PASSWORD') }}"

# ✅ From HashiCorp Vault
db_password: "{{ lookup('hashi_vault', 'secret=secret/db:password') }}"

# ✅ CI/CD secret (injected as env var by the pipeline, same as above but common pattern)
db_password: "{{ lookup('env', 'CI_DB_PASSWORD') }}"
```

## Debugging
```bash
ansible-playbook playbook.yml -v      # Basic verbosity
ansible-playbook playbook.yml -vvv    # Connection debugging
ansible-playbook playbook.yml --check --diff   # Dry-run + diff
ansible-playbook playbook.yml --start-at-task="Install nginx"
ansible-playbook playbook.yml --tags "configuration"
ansible-playbook playbook.yml --skip-tags "testing"
```

```yaml
- name: Show all facts
  ansible.builtin.debug:
    var: ansible_facts

- name: Show specific variable
  ansible.builtin.debug:
    msg: "The value is {{ my_variable }}"
    verbosity: 1   # only visible with -v
```

## Performance Optimization
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
# Disable fact gathering when not needed
- name: Quick task
  hosts: all
  gather_facts: false

# Gather specific facts only (gather_subset is a play-level keyword)
- name: Selective facts
  hosts: all
  gather_facts: true
  gather_subset:
    - '!all'
    - network
```

## Common Modules Reference

### File Operations
- `ansible.builtin.file` – Create directories, symlinks, set permissions
- `ansible.builtin.copy` – Copy static files (use `backup: true` for safety)
- `ansible.builtin.template` – Process Jinja2 templates (use `validate:` for config files)
- `ansible.builtin.lineinfile` – Modify single line in file (use `regexp:` + `line:`)
- `ansible.builtin.blockinfile` – Insert/update multi-line block (set `marker:` to avoid conflicts)
- `ansible.builtin.fetch` – Copy files from remote to local (inverse of `copy`)
- `ansible.builtin.stat` – Get file/directory metadata (check existence, permissions, checksums)

**When to use which:**
- Static file → `copy`
- Dynamic content → `template`
- Single line edit → `lineinfile`
- Multi-line block → `blockinfile`
- Complex edits → `template` (don't fight with lineinfile)

#### File Permissions – always use ugo format
Always set `mode` explicitly using symbolic ugo notation instead of octal (e.g. `'0644'`).
If a party has no permissions at all, use the explicit reset form with `=-`:

```yaml
# ✅ Correct – ugo format
mode: 'u=rw,g=r,o=r'      # equivalent to 0644
mode: 'u=rwx,g=rx,o=rx'   # equivalent to 0755
mode: 'u=rw,g=r,o=-'      # other has NO permissions (not o= or omitted)
mode: 'u=rwx,g=-,o=-'     # only owner has access

# ❌ Wrong – octal format
mode: '0644'
mode: '0755'
```

### Package / Service
- `ansible.builtin.package` – Distro-agnostic package manager (preferred for cross-platform roles)
- `ansible.builtin.apt` – Debian/Ubuntu (always set `update_cache: true` when installing)
- `ansible.builtin.dnf` – RHEL/CentOS 8+ (replaces `yum`)
- `ansible.builtin.yum` – RHEL/CentOS 7 and older (deprecated, use `dnf` for 8+)
- `ansible.builtin.service` – Manage service state and enable/disable (cross-platform)
- `ansible.builtin.systemd` – Systemd-specific features (use `daemon_reload: true` after unit file changes)
- `ansible.builtin.systemd_service` – Alias for `systemd` (same module, different name)

**When to use which:**
- Cross-platform role → `package` + `service`
- Debian-specific → `apt` (for `update_cache`, `autoremove`, etc.)
- RHEL-specific → `dnf` (for `enablerepo`, `disablerepo`, etc.)
- Systemd features → `systemd` (for `daemon_reload`, `masked`, etc.)

### package-latest – never use `state: latest` in production
```yaml
# ❌ package-latest violation – unpredictable, may upgrade unintended packages
- name: Install nginx
  ansible.builtin.package:
    name: nginx
    state: latest

# ✅ Pin the version – predictable and safe
- name: Install nginx
  ansible.builtin.package:
    name: nginx-1.24.0
    state: present

# ✅ If you must update, use update_only/only_upgrade to avoid installing new packages
- name: Update nginx only if already installed
  ansible.builtin.apt:
    name: nginx
    state: latest
    only_upgrade: true
```

### Command Execution
- `ansible.builtin.command` – Run commands without shell processing (preferred, safer)
- `ansible.builtin.shell` – Run commands with shell features (pipes, redirects, wildcards)
- `ansible.builtin.script` – Run local script on remote host
- `ansible.builtin.raw` – Run command without Python (for bootstrapping)

**When to use which:**
- Simple command → `command` (no shell injection risk)
- Pipes/redirects → `shell` (always use `set -o pipefail`)
- Local script → `script` (easier than copying + executing)
- No Python on target → `raw` (only for initial setup)

**Critical rules:**
- Always use `cmd:` key (no free-form)
- Always set `changed_when:` (or `changed_when: false` for read-only)
- Use `creates:` or `removes:` for idempotency when possible
- Prefer Ansible modules over shell commands

```yaml
# command: no shell processing → prefer this
- ansible.builtin.command:
    cmd: /usr/bin/mycommand   # always use cmd: key (no-free-form rule)
  changed_when: false         # when read-only

# shell: only when pipes/redirects are needed
# risky-shell-pipe: always set pipefail when using pipes!
- name: Pipeline with pipefail
  ansible.builtin.shell:
    cmd: |
      set -o pipefail
      cat /etc/hosts | grep localhost
    executable: /bin/bash
  changed_when: false

# shell without pipes: pipefail not required
- ansible.builtin.shell: |
    cd /opt && ./configure && make
  args:
    creates: /opt/app/bin/myapp   # make idempotent!

# script: run local script remotely
- ansible.builtin.script: /local/path/to/script.sh
  args:
    creates: /tmp/script.done
```

## Async Tasks (for long-running operations)
```yaml
- name: Long running operation
  ansible.builtin.command: /usr/bin/long_process
  async: 3600
  poll: 0
  register: long_task

- name: Check on long task
  ansible.builtin.async_status:
    jid: "{{ long_task.ansible_job_id }}"
  register: job_result
  until: job_result.finished
  retries: 30
  delay: 10
```

## Privilege Escalation
```yaml
# For the entire play
- name: System configuration
  hosts: all
  become: true
  become_method: sudo

# Only for individual tasks
- name: Runs as root
  ansible.builtin.package:
    name: nginx
    state: present
  become: true

# partial-become: become_user ALWAYS requires become: true at the SAME level
# ✅ Correct – both defined at task level
- name: Start service as app user
  ansible.builtin.service:
    name: myapp
    state: started
  become: true
  become_user: appuser

# ❌ Wrong – become_user without any become: true
- name: Bad example play
  hosts: all
  tasks:
    - name: Start service as app user
      ansible.builtin.service:
        name: myapp
        state: started
      become_user: appuser  # <- partial-become violation! become: true is missing at the same level
```

## Inventory – Static YAML (recommended)
```yaml
# inventory/production/hosts.yml
---
all:
  children:
    webservers:
      hosts:
        web1.example.com:   # FQDN – no ansible_host needed
        web2.example.com:
      vars:
        nginx_port: 80
    databases:
      hosts:
        db1.example.com:
          postgresql_version: 14
```

## Variable Placement

| File | Precedence | Use for |
|---|---|---|
| `defaults/main.yml` | Low | Public variables – easy to override from outside the role |
| `vars/main.yml` | High | Internal role variables – not meant to be overridden |

Never define role variables at play level or inline in tasks.

## Template Extension

Always use the `.j2` extension for Jinja2 template files stored in the `templates/` folder:
```
templates/
├── nginx.conf.j2
└── app.conf.j2
```

## when Conditions

`when:` must only use Ansible facts or registered variables — never inline shell commands:
```yaml
# ✅ Correct – uses ansible fact
- name: Install on Debian only
  ansible.builtin.package:
    name: nginx
    state: present
  when: ansible_os_family == "Debian"

# ✅ Correct – uses registered variable
- name: Restart only if config changed
  ansible.builtin.service:
    name: nginx
    state: restarted
  when: config_result.changed

# ❌ Wrong – shell command inline in when
- name: Check if file exists
  ansible.builtin.debug:
    msg: "exists"
  when: "{{ lookup('pipe', 'test -f /etc/nginx/nginx.conf') }}"
```

## Tag Strategy

Every play and every task must have at least one tag for targeted execution:
```yaml
tasks:
  - name: Install packages
    ansible.builtin.package:
      name: nginx
      state: present
    tags:
      - packages
      - nginx

  - name: Run tests
    ansible.builtin.command: /usr/local/bin/test_nginx.sh
    tags:
      - never      # NEVER runs automatically
      - testing    # only with --tags testing
```

## Common Issues & Solutions

| Problem | Solution |
|---|---|
| SSH Connection Refused | Set `ansible_user`, `ansible_ssh_private_key_file` |
| Permission Denied | Add `become: true` |
| Module Not Found | `ansible-galaxy collection install community.general` |
| Unreachable Host | Test with `ansible all -m ping -i inventory/hosts.yml` |

## Validation Workflow
```bash
ansible-playbook playbook.yml --syntax-check   # Syntax
ansible-lint playbook.yml                      # Lint
ansible-playbook playbook.yml --check --diff   # Dry-Run
ansible-playbook playbook.yml                  # Execute
```

## ansible-lint Key Rules Reference

| Rule | Profile | What it checks |
|---|---|---|
| `name[missing]` | basic | Every task must have a `name:` |
| `name[casing]` | moderate | Task names must start with uppercase |
| `no-changed-when` | shared | `command`/`shell` tasks must have `changed_when:` |
| `no-free-form` | basic | No inline args on `command`/`shell` — use `cmd:` key |
| `fqcn[action]` | production | Always use FQCN for modules (`ansible.builtin.*`) |
| `var-naming[no-role-prefix]` | basic | Role variables must be prefixed with the role name |
| `yaml[truthy]` | basic | Use `true`/`false` — never `yes`/`no`/`True`/`False` |
| `key-order` | basic | `name` must be first key; `block`/`rescue`/`always` must be last keys |
| `no-handler` | shared | `when: result.changed` → use `notify` + handler instead |
| `partial-become` | basic | `become_user` requires `become: true` at the **same** level |
| `package-latest` | safety | Never `state: latest` in production — pin versions |
| `risky-shell-pipe` | safety | Always `set -o pipefail` when using pipes in `shell:` |
| `risky-file-permissions` | safety | Always set `mode:` explicitly on file-creating modules |
| `avoid-implicit` | safety | No implicit type coercion — use explicit Jinja2 filters |
| `ignore-errors` | shared | Never `ignore_errors: true` without a comment explaining why |
| `no-log-password` | opt-in | Set `no_log: true` when looping over sensitive data |
| `loop-var-prefix` | opt-in | Loop vars in roles must use a prefix (e.g. `__rolename_item`) |
| `import-task-no-when` | production | `when:` on `import_tasks` is evaluated only once — use `include_tasks` |
| `single-entry-point` | production | Roles must have a single `tasks/main.yml` entry point |

## .ansible-lint Configuration

Always include a `.ansible-lint` file in the project root:

```yaml
# .ansible-lint
profile: production   # min, basic, moderate, safety, shared, production

offline: true         # don't fetch schemas on every run

# Opt-in rules (not enabled by default)
enable_list:
  - no-log-password   # warn when secrets are looped without no_log
  - args              # validate module arguments

# Loop variable prefix pattern for roles (avoids collisions)
loop_var_prefix: "^(__|{role}_)"

# Variable naming: lowercase + underscores only
var_naming_pattern: "^[a-z_][a-z0-9_]*$"

# Suppress specific rules per file (prefer this over skip_list)
# .ansible-lint-ignore is the better alternative – see below
skip_list: []

warn_list:
  - experimental
```

Use `.ansible-lint-ignore` for per-file suppressions instead of `skip_list`:
```
# .ansible-lint-ignore
playbooks/legacy.yml package-latest  # pinning not possible for this legacy role
```

## Pre-commit Integration

Add ansible-lint to `.pre-commit-config.yaml` to catch issues before every commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/ansible/ansible-lint
    rev: v25.1.3   # pin to a specific release tag
    hooks:
      - id: ansible-lint
```

Run manually:
```bash
pre-commit run ansible-lint --all-files
```

---
**Remember:** Ansible is about declarative infrastructure — describe the **desired state**, not the steps to get there. Focus on **idempotency**, **clarity**, and **maintainability**.

Docs: https://docs.ansible.com | Galaxy: https://galaxy.ansible.com
