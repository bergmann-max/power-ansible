# Ansible Inventory – Project Conventions

For inventory plugin reference and dynamic-inventory full docs see
<https://docs.ansible.com/ansible/latest/inventory_guide/>.

## Format

- `hosts.ini` for small projects / quick scaffolds.
- `hosts.yml` for nested groups and larger projects.

The MCP tools resolve inventory in this order (see `POWER.md`):
1. `ANSIBLE_INVENTORY` env var
2. `ansible.cfg` `[defaults] inventory =`
3. Fallback paths: `hosts.yml`, `hosts.yaml`, `hosts.ini`, `inventory/hosts.*`

## YAML inventory with environments

Use `children:` to compose environment groups out of functional groups. This
is the recommended layout for any project that has more than one environment.

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

Only set `ansible_host` when the inventory name is **not** the real DNS name —
i.e. an alias, an IP-only host, or a name that differs from the connection
target. Otherwise omit it; the FQDN inventory key is the connection target.

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
- Combined groups via `children:`, not by flattening names where possible.

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

Use the directory form (`group_vars/<group>/vars.yml` + `vault.yml`) whenever
the group has any vault-encrypted variables.

## Multi-inventory (static + dynamic)

Point `inventory =` at a directory; Ansible merges every file inside. Or list
files explicitly with `:` separators.

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

Enable the plugin in `ansible.cfg`:
```ini
[defaults]
inventory = inventory/
enable_plugins = amazon.aws.aws_ec2
```
