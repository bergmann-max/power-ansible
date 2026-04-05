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
  ansible.builtin.command: wget https://example.com/app.tar.gz
  args:
    creates: /opt/app.tar.gz

# ❌ Not idempotent - always executes
- name: Download application
  ansible.builtin.command: wget https://example.com/app.tar.gz

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
    - name: Restart nginx
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
  ansible.builtin.command: /usr/bin/mycommand
  register: result
  failed_when: "'ERROR' in result.stderr"

# Use changed_when to control change status
- name: Check configuration
  ansible.builtin.command: /usr/bin/check_config
  register: config_check
  changed_when: false

# Use blocks for error handling
- name: Handle errors with blocks
  block:
    - name: Risky task
      ansible.builtin.command: /usr/bin/risky_operation
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

### Conditional Execution
```yaml
- name: Install package on RedHat family
  ansible.builtin.yum:
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
  gather_facts: no

# Gather specific facts only
- name: Selective facts
  gather_subset:
    - '!all'
    - network
```

## Common Modules Reference

### File Operations
```yaml
- ansible.builtin.file:       # directories, symlinks, permissions
- ansible.builtin.copy:       # static files (backup: yes recommended)
- ansible.builtin.template:   # Jinja2 (validate: 'nginx -t -c %s')
- ansible.builtin.lineinfile: # single line (regexp + line)
- ansible.builtin.blockinfile: # multi-line block (set marker!)
```

### Package / Service
```yaml
- ansible.builtin.package:    # distro-agnostic (preferred)
- ansible.builtin.apt:        # Debian/Ubuntu (update_cache: yes)
- ansible.builtin.yum:        # RHEL/CentOS
- ansible.builtin.service:    # state + enabled
- ansible.builtin.systemd:    # daemon_reload: yes when needed
```

### Command Execution
```yaml
# command: no shell processing → prefer this
- ansible.builtin.command:
    changed_when: false   # when read-only

# shell: only when pipes/redirects are needed
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
```

## Inventory – Static YAML (recommended)
```yaml
# inventory/production/hosts.yml
---
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 192.168.1.10
        web2.example.com:
          ansible_host: 192.168.1.11
      vars:
        nginx_port: 80
    databases:
      hosts:
        db1.example.com:
          ansible_host: 192.168.1.20
          postgresql_version: 14
```

## Tag Strategy
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

---
**Remember:** Ansible is about declarative infrastructure — describe the **desired state**, not the steps to get there. Focus on **idempotency**, **clarity**, and **maintainability**.

Docs: https://docs.ansible.com | Galaxy: https://galaxy.ansible.com
