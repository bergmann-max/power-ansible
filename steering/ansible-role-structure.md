---
inclusion: fileMatch
fileMatch: ["roles/**/*.yml", "roles/**/*.j2"]
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
  failed_when: false        # if os file doesn't exist, continue
  tags: always

- name: Install {{ role_name }}
  ansible.builtin.include_tasks: install.yml
  tags: install

- name: Configure {{ role_name }}
  ansible.builtin.include_tasks: configure.yml
  tags: configure
```

## defaults/main.yml – Variable Documentation

Every variable MUST be commented:

```yaml
---
# Whether the role is active
nginx_enabled: true

# Package to install
nginx_package: nginx

# Listening port
nginx_port: 80

# Configuration directory
nginx_conf_dir: /etc/nginx

# List of VHosts (show example structure)
nginx_vhosts: []
# nginx_vhosts:
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
