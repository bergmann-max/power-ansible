---
inclusion: fileMatch
fileMatchPattern: "{tasks,handlers,defaults,vars,meta,templates}/**"
---

# Ansible Role Structure & Conventions

## Directory Structure (Required)

```
roles/<role_name>/
├── tasks/
│   ├── main.yml          # Entry point, uses include_tasks
│   ├── install.yml       # Installation tasks
│   ├── configure.yml     # Configuration tasks
│   ├── debian.yml        # OS-specific tasks (optional)
│   └── redhat.yml
├── handlers/
│   └── main.yml
├── defaults/
│   └── main.yml          # Overridable defaults (ALWAYS start here)
├── vars/
│   └── main.yml          # Internal, fixed variables
├── templates/
│   └── *.j2              # Jinja2 templates
├── files/
│   └── *                 # Static files
├── meta/
│   └── main.yml          # Dependencies, Galaxy metadata
└── README.md
```

## tasks/main.yml – Always Build Modularly

```yaml
---
- name: Include OS-specific variables
  ansible.builtin.include_vars: "{{ ansible_os_family | lower }}.yml"
  when: ansible_os_family is defined   # skip gracefully if fact is unavailable
  tags: always

- name: Install {{ role_name }}
  ansible.builtin.include_tasks: install.yml
  tags: install

- name: Configure {{ role_name }}
  ansible.builtin.include_tasks: configure.yml
  tags: configure
```

### import_tasks vs include_tasks – when to use which

| | `import_tasks` | `include_tasks` |
|---|---|---|
| Processed | at parse time (static) | at runtime (dynamic) |
| `when:` on the directive | ❌ evaluated only once for all tasks inside | ✅ evaluated at runtime |
| Tags on included tasks | ✅ visible to `--list-tags` | ❌ not visible until runtime |
| Use when | no conditions needed, want tag visibility | OS-specific includes, conditional loading |

```yaml
# ✅ include_tasks for conditional/dynamic loading
- name: Include OS-specific tasks
  ansible.builtin.include_tasks: "{{ ansible_os_family | lower }}.yml"
  when: ansible_os_family is defined

# ✅ import_tasks for unconditional static includes (tags work correctly)
- name: Import hardening tasks
  ansible.builtin.import_tasks: hardening.yml

# ❌ import-task-no-when violation – when: on import_tasks applies only once
- name: Import tasks conditionally
  ansible.builtin.import_tasks: optional.yml
  when: some_condition   # <- use include_tasks instead!
```

## ansible-lint Rules to Follow

### name[missing] – every task needs a name
```yaml
# ✅
- name: Install package
  ansible.builtin.package:
    name: nginx
    state: present

# ❌ ansible-lint will fail
- ansible.builtin.package:
    name: nginx
    state: present
```

### name[casing] – task names must start with uppercase
```yaml
# ✅
- name: Install nginx package

# ❌
- name: install nginx package
```

### no-changed-when – command/shell always need changed_when
```yaml
# ✅
- name: Check app version
  ansible.builtin.command:
    cmd: /usr/bin/myapp --version
  register: app_version
  changed_when: false   # read-only, never marks as changed

- name: Run migration
  ansible.builtin.command:
    cmd: /usr/bin/migrate
  changed_when: app_version.rc == 0   # explicit condition

# ❌ ansible-lint will fail
- name: Run something
  ansible.builtin.command:
    cmd: /usr/bin/something
```

### no-free-form – never use free-form command syntax
```yaml
# ✅
- name: Run script
  ansible.builtin.command:
    cmd: /usr/bin/myscript --arg value

# ❌
- name: Run script
  ansible.builtin.command: /usr/bin/myscript --arg value
```
### key-order – recommended task key order

ansible-lint enforces only that `name` is the first key, and that `block`/`rescue`/`always` are the last keys. The order below is a widely-used convention that also satisfies the rule:

```yaml
- name: ...          # 1. name first (enforced by lint)
  module:            # 2. module
    ...
  when: ...          # 3. conditionals (must come before block/rescue/always)
  loop: ...          # 4. loops
  register: ...      # 5. register
  notify: ...        # 6. notify
  tags: ...          # 7. tags
  block: ...         # 8. block/rescue/always LAST (enforced by lint)
```

## Variable Naming – Role Prefix

ansible-lint enforces `var-naming[no-role-prefix]`: every variable defined in a role MUST be prefixed with the role name. This avoids collisions when multiple roles are used together.

```yaml
# Role: install_nginx  →  all variables must start with install_nginx_
install_nginx_port: 80
install_nginx_conf_dir: /etc/nginx
install_nginx_vhosts: []
```

No generic names like `port`, `enabled`, or `package` — always `<role_name>_<variable>`.

## Loop Variables – loop_var_prefix

When using loops inside roles, the default loop variable `item` can collide with outer loops. Use `loop_control` with a role-specific prefix to avoid this (`loop-var-prefix` rule, enabled via `.ansible-lint`):

```yaml
# ✅ Role-prefixed loop variable – no collision with outer loops
- name: Create vhosts
  ansible.builtin.template:
    src: vhost.conf.j2
    dest: "/etc/nginx/conf.d/{{ __nginx_vhost.name }}.conf"
    mode: 'u=rw,g=r,o=r'
  loop: "{{ nginx_vhosts }}"
  loop_control:
    loop_var: __nginx_vhost   # prefix: __ or <role_name>_
    label: "{{ __nginx_vhost.name }}"

# ❌ Generic 'item' – risky in nested/included roles
- name: Create vhosts
  ansible.builtin.template:
    src: vhost.conf.j2
    dest: "/etc/nginx/conf.d/{{ item.name }}.conf"
  loop: "{{ nginx_vhosts }}"
```

Configure the expected pattern in `.ansible-lint`:
```yaml
loop_var_prefix: "^(__|{role}_)"
```

## defaults/main.yml – Variable Documentation

Every variable MUST be commented and MUST use the role name as prefix:

```yaml
---
# Role: my_role  →  all variables prefixed with my_role_

# Whether the role is active
my_role_enabled: true

# Package to install
my_role_package: myapp

# Listening port
my_role_port: 80

# Configuration directory
my_role_conf_dir: /etc/myapp

# List of vhosts (show example structure)
my_role_vhosts: []
# my_role_vhosts:
#   - name: example.com
#     port: 80
#     root: /var/www/example
```

## Jinja2 Templates – Required Header

Every `.j2` file starts with:

```
{# Managed by Ansible – role: {{ role_name }} #}
{# Manual changes will be overwritten on the next Ansible run! #}
```

## Handlers – Correct Usage

```yaml
# handlers/main.yml
---
- name: restart nginx           # Name = exactly the string in `notify:`
  ansible.builtin.service:
    name: nginx
    state: restarted
  listen: "restart nginx"       # listen allows multiple tasks to trigger

- name: reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
  listen: "reload nginx"
```

## meta/main.yml – Declare Dependencies

```yaml
---
dependencies:
  - role: common          # Role in the same project
  - role: geerlingguy.git # Galaxy role (must be in requirements.yml!)
    vars:
      git_version: "2.40"
```
