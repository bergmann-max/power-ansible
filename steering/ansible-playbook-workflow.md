---
inclusion: fileMatch
fileMatchPattern: "{playbooks/**/*.yml,site.yml,*.playbook.yml}"
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
    # No passwords here! → ansible-vault, env vars, CI/CD secrets, or external secret managers (e.g. HashiCorp Vault)

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
- Format: `Verb + Object` → "Install nginx", "Configure sshd", "Start application"
- Language: English
- No abbreviations: `Configure` not `Cfg`
- ansible-lint `name[casing]`: first letter MUST be uppercase
- ansible-lint `name[missing]`: every task MUST have a `name:`

## no-free-form – never use inline command syntax
```yaml
# ✅
- name: Run migration
  ansible.builtin.command:
    cmd: /usr/bin/migrate --env production

# ❌ ansible-lint will fail
- name: Run migration
  ansible.builtin.command: /usr/bin/migrate --env production
```

## What NEVER Belongs in a Playbook
- Passwords in plain text → `ansible-vault encrypt_string` or manage externally (CI/CD secrets, HashiCorp Vault, etc.) and pass via `-e`
- `ignore_errors: true` without a comment explaining why
- `shell:` or `command:` when an Ansible module exists
- `yes`/`no`/`True`/`False` as booleans → always use `true`/`false` (`yaml[truthy]`)

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
