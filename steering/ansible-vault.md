# Ansible Vault – Project Conventions

Full vault CLI ref:
<https://docs.ansible.com/ansible/latest/vault_guide/index.html>.

## When to use vault

Vault for **static secrets** in repo: DB passwords, API tokens, SSH/TLS private keys.

Do **not** use vault for:
- Non-sensitive config (ports, paths, package names).
- Public certificates.
- Frequently rotating secrets → external secret manager.

## Layout — separate `vars.yml` + `vault.yml`

Only layout used here. No inline `!vault` blobs.

```
group_vars/
└── all/
    ├── vars.yml       # plain
    └── vault.yml      # encrypted
```

`vars.yml` references vault vars by `vault_*` prefix; `vault.yml` defines them. Diffs stay readable; encrypted file changes only when secret changes.

```yaml
# vars.yml
db_host: db.example.com
db_port: 5432
db_user: app_user
db_password: "{{ vault_db_password }}"

# vault.yml (encrypted)
vault_db_password: "supersecret123"
vault_api_key: "abc123xyz"
```

## CLI cheatsheet

| Command | Use |
|---|---|
| `ansible-vault create <file>` | new encrypted file |
| `ansible-vault edit <file>` | edit in place |
| `ansible-vault view <file>` | read without decrypt |
| `ansible-vault encrypt <file>` | encrypt existing plain file |
| `ansible-vault decrypt <file>` | decrypt (writes plain text) |
| `ansible-vault rekey <file>` | change password |
| `ansible-vault encrypt_string 'val' --name 'k'` | one-off inline blob |

### `encrypt_string` from stdin (CI-friendly, avoids shell history)

```bash
echo -n 'supersecret123' | ansible-vault encrypt_string --stdin-name 'vault_api_key'
```

## Password sources

Preference order:

1. `vault_password_file = ~/.vault_pass` in `ansible.cfg` (dev machine, `chmod 600`).
2. `--vault-password-file <path>` in CI, written from CI secret to temp file, removed after run.
3. `--ask-vault-pass` only for ad-hoc/one-off.

Script-based password (fetched from env var):

```bash
#!/bin/bash
# ~/.vault_pass.sh — chmod 700
echo "$VAULT_PASSWORD"
```

```bash
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass.sh
```

## Vault IDs for multi-env

```bash
ansible-vault create --vault-id prod@prompt group_vars/production/vault.yml
ansible-vault create --vault-id stg@prompt  group_vars/staging/vault.yml

ansible-playbook playbook.yml \
  --vault-id prod@~/.vault_pass_prod \
  --vault-id stg@~/.vault_pass_stg
```

## CI/CD integration

### GitHub Actions

```yaml
- name: Run Ansible playbook
  env:
    VAULT_PASSWORD: ${{ secrets.ANSIBLE_VAULT_PASSWORD }}
  run: |
    echo "$VAULT_PASSWORD" > /tmp/vault_pass
    ansible-playbook playbook.yml --vault-password-file /tmp/vault_pass
    rm -f /tmp/vault_pass
```

### GitLab CI

```yaml
deploy:
  variables:
    VAULT_PASSWORD: $ANSIBLE_VAULT_PASSWORD
  script:
    - echo "$VAULT_PASSWORD" > /tmp/vault_pass
    - ansible-playbook playbook.yml --vault-password-file /tmp/vault_pass
    - rm -f /tmp/vault_pass
```

### Jenkins

```groovy
withCredentials([string(credentialsId: 'ansible-vault-password', variable: 'VAULT_PASS')]) {
    sh '''
        echo "$VAULT_PASS" > /tmp/vault_pass
        ansible-playbook playbook.yml --vault-password-file /tmp/vault_pass
        rm -f /tmp/vault_pass
    '''
}
```

## External secret managers (alternative to vault)

Dynamic/rotating secrets: use lookups, not encrypted files.

### HashiCorp Vault — requires `hvac`

```yaml
- name: Fetch DB password
  ansible.builtin.set_fact:
    db_password: "{{ lookup('hashi_vault', 'secret=secret/data/db:password') }}"
  no_log: true
```

### AWS Secrets Manager — requires `boto3`

```yaml
- name: Fetch API key from AWS
  ansible.builtin.set_fact:
    api_key: "{{ lookup('amazon.aws.aws_secret', 'prod/api_key', region='us-east-1') }}"
  no_log: true
```

### Azure Key Vault — requires `azure-keyvault-secrets`

```yaml
- name: Fetch DB password from Azure
  ansible.builtin.set_fact:
    db_password: "{{ lookup('azure.azcollection.azure_keyvault_secret', 'db-password', vault_url='https://myvault.vault.azure.net') }}"
  no_log: true
```

## Rules

1. Never commit `vault_pass*` files — add to `.gitignore`:
   ```
   **/vault_pass*
   **/.vault_pass*
   ```
2. Tasks consuming secret get `no_log: true`:
   ```yaml
   - name: Create database user
     community.postgresql.postgresql_user:
       name: app_user
       password: "{{ vault_db_password }}"
     no_log: true
   ```
3. Rotate vault password on personnel changes: `ansible-vault rekey <file>`.
4. After editing vault file, sanity-check:
   ```bash
   ansible-vault view group_vars/all/vault.yml
   ansible-playbook playbook.yml --syntax-check --ask-vault-pass
   ```

## Common errors

- **"Decryption failed"** → wrong password, or missing `--vault-id` when multiple IDs in use.
- **"unhexlify error"** → file edited outside `ansible-vault edit` while encrypted; restore from backup.
- **"no vault secrets found"** → no password source configured (cfg / flag / prompt).
