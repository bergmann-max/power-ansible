# Ansible Collections – Project Conventions

Project pin all non-builtin collections in `requirements.yml`. Full docs:
<https://docs.ansible.com/ansible/latest/collections_guide/> and
<https://galaxy.ansible.com>.

## Rules

1. **Always FQCN** (`namespace.collection.module`) — never bare module name or `collections:` keyword on play.
2. **Pin in `requirements.yml`** — exact version (`"8.6.0"`) or minimum (`">=8.0.0"`). Never unpinned.
3. **Declare collection deps in role meta** (`roles/<name>/meta/main.yml`) when role uses non-builtin modules.
4. **Document Python deps** — many collections need extra pip packages; list in role/playbook README.

## `requirements.yml` shape

```yaml
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

roles:
  - name: geerlingguy.nginx
    version: "3.1.4"
```

Install: `ansible-galaxy install -r requirements.yml`

## Role meta declaration

```yaml
# roles/<role>/meta/main.yml
---
dependencies: []
collections:
  - community.general
  - ansible.posix
```

## Popular collections — module catalog

LLM agents: do **not** invent module names. Verify with `ansible-doc -l <collection>`.

### `community.general`
General-purpose modules outside `ansible.builtin`:
- `community.general.docker_container` — manage containers
- `community.general.npm` — npm packages
- `community.general.terraform` — run Terraform
- `community.general.htpasswd` — htpasswd files
- `community.general.ini_file` — edit INI files
- `community.general.archive` — create archives

### `ansible.posix`
POSIX-specific ops:
- `ansible.posix.firewalld` — firewalld zones/rules
- `ansible.posix.selinux` — SELinux state
- `ansible.posix.mount` — mount points (`/etc/fstab` + live)
- `ansible.posix.sysctl` — kernel params
- `ansible.posix.authorized_key` — SSH authorized_keys

### `amazon.aws`
Needs `pip install boto3 botocore`.
- `amazon.aws.ec2_instance` — EC2 instances
- `amazon.aws.s3_bucket` / `s3_object` — S3
- `amazon.aws.rds_instance` — RDS databases
- `amazon.aws.iam_role` / `iam_user` — IAM
- `amazon.aws.cloudformation` — stacks

### `community.docker`
Needs `pip install docker`.
- `community.docker.docker_container`
- `community.docker.docker_image`
- `community.docker.docker_network`
- `community.docker.docker_compose_v2`

### `kubernetes.core`
Needs `pip install kubernetes`.
- `kubernetes.core.k8s` — apply/delete K8s resources
- `kubernetes.core.helm` — Helm charts
- `kubernetes.core.k8s_info` — query resources

### `community.postgresql`
Needs `pip install psycopg2-binary`.
- `community.postgresql.postgresql_db`
- `community.postgresql.postgresql_user`
- `community.postgresql.postgresql_query`
- `community.postgresql.postgresql_privs`

### `community.mysql`
Needs `pip install PyMySQL`.
- `community.mysql.mysql_db`
- `community.mysql.mysql_user`
- `community.mysql.mysql_query`

## Usage example

```yaml
- name: Install nginx container
  community.docker.docker_container:
    name: nginx
    image: nginx:1.27.0
    state: started
    ports: ["80:80"]
```

## Custom collection — skeleton

Only when extracting in-repo modules into distributable package.

```bash
ansible-galaxy collection init my_namespace.my_collection
```

```
my_namespace/my_collection/
├── galaxy.yml        # namespace, name, version, deps
├── README.md
├── plugins/{modules,inventory,lookup,filter}/
├── roles/
├── playbooks/
└── tests/
```

Build + install locally:
```bash
ansible-galaxy collection build
ansible-galaxy collection install my_namespace-my_collection-1.0.0.tar.gz
```

## CLI quick reference

| Command | Use |
|---|---|
| `ansible-galaxy collection install <name>` | install single collection |
| `ansible-galaxy collection install -r requirements.yml` | install from file |
| `ansible-galaxy collection install -r requirements.yml --upgrade` | update existing |
| `ansible-galaxy collection list` | list installed |
| `ansible-doc <ns>.<col>.<mod>` | module docs |
| `ansible-doc -l <ns>.<col>` | list all modules in collection |
| `ansible-galaxy collection build` | build tarball |
| `ansible-galaxy collection publish <tarball>` | publish to Galaxy |

## Troubleshooting

- **"Module not found"** → collection missing or wrong FQCN. Check `ansible-galaxy collection list` and `ansible-doc -l <collection>`.
- **Version conflict** → multiple paths have same collection. Check `collections_path` in `ansible.cfg`.
- **"Python library missing"** → install collection's pip deps (table above).
