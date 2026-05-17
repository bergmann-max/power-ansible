# Ansible Inventory – Project Conventions

Inventory plugin reference + dynamic-inventory docs:
<https://docs.ansible.com/ansible/latest/inventory_guide/>.

## Format

- `hosts.ini` for small projects / quick scaffolds.
- `hosts.yml` for nested groups + larger projects.

MCP tools resolve inventory this order (see `POWER.md`):
1. `ANSIBLE_INVENTORY` env var
2. `ansible.cfg` `[defaults] inventory =`
3. Fallback paths: `hosts.yml`, `hosts.yaml`, `hosts.ini`, `inventory/hosts.*`

## YAML inventory with environments

Use `children:` compose environment groups from functional groups. Recommended layout for any project with >1 environment.

```yaml
# inventory/hosts.yml
---
all:
  children:
    webservers:
      hosts:
        web01.example.com:    # FQDN as the inventory key — no ansible_host needed
        web02.example.com:
      vars:
        nginx_port: 80

    dbservers:
      hosts:
        db01.example.com:
          postgresql_version: 14

    production:
      children:
        webservers:
        dbservers:

    staging:
      hosts:
        staging01.example.com:
```

## `ansible_host` rule

Set `ansible_host` only when inventory name **not** real DNS name — alias, IP-only host, or name differs from connection target. Else omit; FQDN inventory key = connection target.

```yaml
all:
  hosts:
    db-primary:                        # logical alias
      ansible_host: db01.example.com
    legacy-app:
      ansible_host: 10.0.3.15          # no DNS entry
```

## Group naming

- Lowercase, underscores: `web_servers`, not `WebServers`.
- Functional groups: `webservers`, `dbservers`, `loadbalancers`.
- Environment groups: `production`, `staging`, `development`.
- Combine via `children:`, not flattened names.

## Vars layout

```
inventory/
├── hosts.yml
├── group_vars/
│   ├── all.yml
│   ├── all/                # split when using vault
│   │   ├── vars.yml
│   │   └── vault.yml
│   └── webservers.yml
└── host_vars/
    └── web01.example.com/
        ├── vars.yml
        └── vault.yml
```

Use directory form (`group_vars/<group>/vars.yml` + `vault.yml`) whenever group has vault-encrypted vars.

## Multi-inventory (static + dynamic)

Point `inventory =` at directory; Ansible merges every file inside. Or list files explicitly with `:` separators.

```ini
# ansible.cfg
[defaults]
inventory = inventory/                                # directory mode
# or
inventory = inventory/static/hosts.yml:inventory/aws_ec2.yml
```

## Dynamic inventory

Use plugins, not legacy scripts.

```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions: [eu-central-1]
filters:
  instance-state-name: running
keyed_groups:
  - { key: tags.Role, prefix: role }
  - { key: tags.Environment, prefix: env }
compose:
  ansible_host: public_ip_address
```

Enable plugin in `ansible.cfg`:
```ini
[defaults]
inventory = inventory/
enable_plugins = amazon.aws.aws_ec2
```
