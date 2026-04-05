---
inclusion: fileMatch
fileMatch: ["playbooks/**/*.yml", "site.yml", "*.playbook.yml"]
---

# Ansible Playbook Workflow

## Required Structure of Every Playbook

```yaml
---
- name: <Short, precise description>
  hosts: <group_or_host>
  gather_facts: true          # set explicitly
  become: false               # only true if root is strictly required
  tags:
    - <playbook-name>

  vars:
    # No passwords here! → ansible-vault or env vars

  pre_tasks:
    - name: Assert prerequisites
      ansible.builtin.assert:
        that: [...]
      tags: always

  tasks:
    - name: <Verb + Noun, e.g. "Install nginx package">
      ansible.builtin.<module>:
        ...
      tags: [...]
      notify: <handler if needed>

  handlers:
    - name: <lowercase, descriptive>
      ansible.builtin.service:
        ...
```

## Task Naming Conventions
- **Format**: `Verb + Object` → "Install nginx", "Configure sshd", "Start application"
- **Language**: English
- **No abbreviations**: `Configure` not `Cfg`

## What NEVER Belongs in a Playbook
- Passwords in plain text → `ansible-vault encrypt_string` or manage externally (CI/CD secrets, HashiCorp Vault, etc.) and pass via `-e`
- `ignore_errors: true` without a comment explaining why
- `shell:` or `command:` when an Ansible module exists
- `always_run: yes` (deprecated) → `tags: always`

## Tags Strategy
Every play and every task gets tags:
```yaml
tags:
  - install     # for installation tasks
  - configure   # for configuration tasks
  - service     # for service management
  - never       # for tasks that should only run explicitly
```

## Idempotency Checklist
Check before committing:
- [ ] Does the playbook run twice without errors and without unwanted changes?
- [ ] Are all `command:`/`shell:` tasks annotated with `changed_when:` and `failed_when:`?
- [ ] Are files with `state: present` not constantly being rewritten?
