---
inclusion: fileMatch
fileMatchPattern: "{inventory/**,group_vars/**,host_vars/**,**/hosts.yml,**/hosts.ini}"
---

# Ansible Inventory Conventions

## Inventory Format: INI vs. YAML

Both formats are fully supported. Choose based on your project size and preference:

- `hosts.ini` – simple, compact, good for small projects and quick scaffolding
- `hosts.yml` – more expressive, better for complex group hierarchies and larger projects

### INI (default for scaffolding)
```ini
[webservers]
web01.example.com
web02.example.com

[dbservers]
db01.example.com
```

## YAML Structure (recommended for larger projects)

```yaml
# inventory/hosts.yml
---
all:
  children:
    webservers:
      hosts:
        web01.example.com:   # FQDN as name – no ansible_host needed
        web02.example.com:
    dbservers:
      hosts:
        db01.example.com:

    # Environment groups
    production:
      children:
        webservers:
        dbservers:
    staging:
      hosts:
        staging01.example.com:
```

### When to use `ansible_host`

`ansible_host` is only needed when the inventory name is not directly reachable — e.g. a logical alias, a host without a DNS entry, or an internal hostname that differs from the connection target.

```yaml
# ansible_host useful: alias in inventory, connecting via IP or different hostname
all:
  hosts:
    db-primary:                        # logical name in inventory
      ansible_host: db01.example.com   # actual hostname used for the connection
    legacy-app:
      ansible_host: 10.0.3.15          # no DNS entry available
```

## group_vars/ Structure

```
inventory/
└── group_vars/
    ├── all.yml             # Applies to all hosts
    ├── all/                # Split into multiple files (when using Vault)
    │   ├── vars.yml
    │   └── vault.yml       # ansible-vault encrypted
    ├── webservers.yml
    ├── dbservers.yml
    └── production.yml
```

## host_vars/ – Host-specific Variables

```
inventory/
└── host_vars/
    └── web01.example.com/
        ├── vars.yml
        └── vault.yml
```

## ansible.cfg Inventory Setting

```ini
[defaults]
inventory = inventory/hosts.yml
```

Or multiple inventories:
```ini
inventory = inventory/production:inventory/staging
```

## Naming Conventions for Groups
- Lowercase, underscores: `web_servers` ✅, `WebServers` ❌
- Functional: `webservers`, `dbservers`, `loadbalancers`
- Environment: `production`, `staging`, `development`
- Combined (child groups): `prod_webservers`

## Dynamic Inventory

For cloud environments or frequently changing infrastructure, use dynamic inventory scripts or plugins instead of static files.

### Plugin-based (recommended)
```yaml
# inventory/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - eu-central-1
filters:
  instance-state-name: running
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: tags.Environment
    prefix: env
compose:
  ansible_host: public_ip_address
```

```ini
# ansible.cfg
[defaults]
inventory = inventory/aws_ec2.yml
enable_plugins = amazon.aws.aws_ec2
```

### Mixing Static and Dynamic
```ini
# ansible.cfg – comma-separated or directory-based
[defaults]
inventory = inventory/static/hosts.yml:inventory/aws_ec2.yml
```

Or use a directory — Ansible merges all files automatically:
```
inventory/
├── static_hosts.yml      # static
├── aws_ec2.yml           # dynamic plugin
└── group_vars/
    └── all.yml
```
