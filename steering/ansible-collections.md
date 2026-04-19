---
inclusion: fileMatch
fileMatchPattern: "{requirements.yml,collections/requirements.yml,galaxy.yml}"
---

# Ansible Collections – Community Modules & Roles

## Overview
Ansible Collections bundle modules, plugins, roles, and playbooks into distributable packages. They extend Ansible beyond `ansible.builtin.*` modules.

## Core Concepts

### What is a Collection?
A collection is a distribution format for Ansible content:
- **Modules** – Task plugins (e.g. `community.general.docker_container`)
- **Roles** – Reusable task bundles
- **Plugins** – Inventory, lookup, filter, callback plugins
- **Playbooks** – Example playbooks

### Namespace Format
Collections use FQCN (Fully Qualified Collection Name):
```
namespace.collection.module
```

Examples:
- `ansible.builtin.copy` – Built-in module (always available)
- `community.general.docker_container` – Community collection
- `amazon.aws.ec2_instance` – AWS collection

## Installing Collections

### requirements.yml (recommended)
```yaml
# requirements.yml
---
collections:
  - name: community.general
    version: ">=8.0.0"
  - name: ansible.posix
    version: ">=1.5.0"
  - name: amazon.aws
    version: ">=9.0.0"
  - name: community.docker
    version: ">=3.0.0"
```

Install:
```bash
ansible-galaxy collection install -r requirements.yml
```

### Install single collection
```bash
ansible-galaxy collection install community.general
ansible-galaxy collection install community.general:8.6.0  # specific version
```

### Install from Git
```yaml
# requirements.yml
collections:
  - name: https://github.com/ansible-collections/community.general.git
    type: git
    version: main
```

### Install to custom path
```bash
ansible-galaxy collection install -r requirements.yml -p ./collections
```

Configure in `ansible.cfg`:
```ini
[defaults]
collections_path = ./collections:~/.ansible/collections:/usr/share/ansible/collections
```

## Using Collections in Playbooks

### FQCN (recommended)
```yaml
- name: Install Docker container
  community.docker.docker_container:
    name: nginx
    image: nginx:latest
    state: started
```

### collections keyword (shorthand)
```yaml
- name: Docker tasks
  hosts: all
  collections:
    - community.docker
  tasks:
    - name: Install container
      docker_container:  # no FQCN needed
        name: nginx
        image: nginx:latest
```

**Warning:** `collections:` keyword can cause ambiguity if multiple collections have the same module name. Always prefer FQCN.

## Popular Collections

### community.general
General-purpose modules not in `ansible.builtin`:
- `community.general.docker_container` – Manage Docker containers
- `community.general.npm` – Manage npm packages
- `community.general.terraform` – Run Terraform
- `community.general.htpasswd` – Manage htpasswd files
- `community.general.ini_file` – Edit INI files

```yaml
collections:
  - name: community.general
    version: ">=8.0.0"
```

### ansible.posix
POSIX-specific modules:
- `ansible.posix.firewalld` – Manage firewalld
- `ansible.posix.selinux` – Manage SELinux
- `ansible.posix.mount` – Manage mount points
- `ansible.posix.sysctl` – Manage kernel parameters

```yaml
collections:
  - name: ansible.posix
    version: ">=1.5.0"
```

### amazon.aws
AWS modules:
- `amazon.aws.ec2_instance` – Manage EC2 instances
- `amazon.aws.s3_bucket` – Manage S3 buckets
- `amazon.aws.rds_instance` – Manage RDS databases
- `amazon.aws.iam_role` – Manage IAM roles

```yaml
collections:
  - name: amazon.aws
    version: ">=9.0.0"
```

Requires `boto3` and `botocore`:
```bash
pip install boto3 botocore
```

### community.docker
Docker-specific modules:
- `community.docker.docker_container` – Manage containers
- `community.docker.docker_image` – Manage images
- `community.docker.docker_network` – Manage networks
- `community.docker.docker_compose` – Manage Docker Compose

```yaml
collections:
  - name: community.docker
    version: ">=3.0.0"
```

Requires `docker` Python library:
```bash
pip install docker
```

### kubernetes.core
Kubernetes modules:
- `kubernetes.core.k8s` – Manage Kubernetes resources
- `kubernetes.core.helm` – Manage Helm charts
- `kubernetes.core.k8s_info` – Query Kubernetes resources

```yaml
collections:
  - name: kubernetes.core
    version: ">=5.0.0"
```

Requires `kubernetes` Python library:
```bash
pip install kubernetes
```

### community.postgresql
PostgreSQL modules:
- `community.postgresql.postgresql_db` – Manage databases
- `community.postgresql.postgresql_user` – Manage users
- `community.postgresql.postgresql_query` – Run SQL queries

```yaml
collections:
  - name: community.postgresql
    version: ">=3.0.0"
```

Requires `psycopg2`:
```bash
pip install psycopg2-binary
```

### community.mysql
MySQL/MariaDB modules:
- `community.mysql.mysql_db` – Manage databases
- `community.mysql.mysql_user` – Manage users
- `community.mysql.mysql_query` – Run SQL queries

```yaml
collections:
  - name: community.mysql
    version: ">=3.0.0"
```

Requires `PyMySQL`:
```bash
pip install PyMySQL
```

## Creating a Collection

### Initialize collection structure
```bash
ansible-galaxy collection init my_namespace.my_collection
```

Structure:
```
my_namespace/my_collection/
├── galaxy.yml              # Collection metadata
├── README.md
├── plugins/
│   ├── modules/            # Custom modules
│   ├── inventory/          # Inventory plugins
│   ├── lookup/             # Lookup plugins
│   └── filter/             # Filter plugins
├── roles/                  # Roles bundled with collection
├── playbooks/              # Example playbooks
└── tests/                  # Integration tests
```

### galaxy.yml
```yaml
namespace: my_namespace
name: my_collection
version: 1.0.0
readme: README.md
authors:
  - Your Name <you@example.com>
description: My custom Ansible collection
license:
  - MIT
tags:
  - infrastructure
  - automation
dependencies:
  community.general: ">=8.0.0"
repository: https://github.com/yourname/my_collection
documentation: https://docs.example.com
homepage: https://example.com
issues: https://github.com/yourname/my_collection/issues
```

### Build and install locally
```bash
ansible-galaxy collection build
ansible-galaxy collection install my_namespace-my_collection-1.0.0.tar.gz
```

## Best Practices

### 1. Pin collection versions
```yaml
# ✅ Correct – pinned version
collections:
  - name: community.general
    version: "8.6.0"

# ⚠️ Acceptable – minimum version
collections:
  - name: community.general
    version: ">=8.0.0"

# ❌ Wrong – no version (unpredictable)
collections:
  - name: community.general
```

### 2. Always use FQCN in tasks
```yaml
# ✅ Correct – explicit FQCN
- name: Manage Docker container
  community.docker.docker_container:
    name: nginx
    state: started

# ❌ Wrong – ambiguous short name
- name: Manage Docker container
  docker_container:
    name: nginx
    state: started
```

### 3. Document collection dependencies
```yaml
# roles/my_role/meta/main.yml
---
dependencies: []
collections:
  - community.general
  - ansible.posix
```

### 4. Use requirements.yml for all collections
```yaml
# requirements.yml
---
collections:
  - name: community.general
    version: ">=8.0.0"
  - name: ansible.posix
    version: ">=1.5.0"

roles:
  - name: geerlingguy.nginx
    version: "3.1.4"
```

Install both collections and roles:
```bash
ansible-galaxy install -r requirements.yml
```

### 5. Check collection documentation
```bash
ansible-doc community.general.docker_container
ansible-doc -l community.general  # list all modules in collection
```

### 6. Verify collection installation
```bash
ansible-galaxy collection list
ansible-galaxy collection list community.general
```

### 7. Update collections regularly
```bash
ansible-galaxy collection install -r requirements.yml --upgrade
```

## Common Issues

### "Module not found"
- Collection not installed: `ansible-galaxy collection install <name>`
- Wrong FQCN: check `ansible-doc -l <collection>`
- Collections path not configured: check `ansible.cfg`

### "Collection version conflict"
- Multiple versions installed in different paths
- Check: `ansible-galaxy collection list`
- Remove old versions: `rm -rf ~/.ansible/collections/ansible_collections/<namespace>/<collection>`

### "Python library missing"
Many collections require Python libraries:
- `amazon.aws` → `boto3`, `botocore`
- `community.docker` → `docker`
- `kubernetes.core` → `kubernetes`
- `community.postgresql` → `psycopg2`

Install with pip:
```bash
pip install boto3 docker kubernetes psycopg2-binary
```

## Quick Reference

| Command | Description |
|---|---|
| `ansible-galaxy collection install <name>` | Install collection |
| `ansible-galaxy collection install -r requirements.yml` | Install from requirements file |
| `ansible-galaxy collection list` | List installed collections |
| `ansible-galaxy collection list <name>` | Show specific collection version |
| `ansible-doc <namespace>.<collection>.<module>` | Show module documentation |
| `ansible-doc -l <namespace>.<collection>` | List all modules in collection |
| `ansible-galaxy collection build` | Build collection tarball |
| `ansible-galaxy collection publish <tarball>` | Publish to Galaxy |

---
**Remember:** Collections extend Ansible's capabilities. Always pin versions, use FQCN, and document dependencies in `requirements.yml`.

Docs: https://docs.ansible.com/ansible/latest/collections_guide/index.html
Galaxy: https://galaxy.ansible.com
