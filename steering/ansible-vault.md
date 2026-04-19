---
inclusion: fileMatch
fileMatchPattern: "{group_vars/**/*vault*,host_vars/**/*vault*,**/*vault*.yml}"
---

# Ansible Vault – Secret Management

## Overview
Ansible Vault encrypts sensitive data (passwords, API keys, certificates) so they can be safely committed to version control.

## Core Concepts

### When to Use Vault
- Database passwords
- API tokens and keys
- SSL/TLS private keys
- SSH private keys
- Any credential that should not be in plain text

### When NOT to Use Vault
- Non-sensitive configuration (ports, paths, package names)
- Public certificates (only private keys need encryption)
- Data that changes frequently (use external secret managers instead)

## Vault File Structure

### Option 1: Separate vault file (recommended)
```
group_vars/
├── all/
│   ├── vars.yml       # plain text variables
│   └── vault.yml      # encrypted secrets only
└── webservers/
    ├── vars.yml
    └── vault.yml
```

**vars.yml** (plain text):
```yaml
---
db_host: db.example.com
db_port: 5432
db_name: production
db_user: app_user
db_password: "{{ vault_db_password }}"  # reference to vault variable
```

**vault.yml** (encrypted):
```yaml
---
vault_db_password: "supersecret123"
vault_api_key: "abc123xyz"
```

### Option 2: Inline encrypted strings
```yaml
---
# group_vars/all.yml
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  66386439653765386661326634323061636537653537646462383762386463376534613765396330
  ...
```

## Encrypting Secrets

### Encrypt entire file
```bash
ansible-vault create group_vars/all/vault.yml
ansible-vault encrypt group_vars/all/vault.yml
ansible-vault edit group_vars/all/vault.yml
ansible-vault view group_vars/all/vault.yml
```

### Encrypt single string (recommended for inline secrets)
```bash
ansible-vault encrypt_string 'supersecret123' --name 'vault_db_password'
```

Output:
```yaml
vault_db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  66386439653765386661326634323061636537653537646462383762386463376534613765396330
  ...
```

Copy this directly into your vars file.

### Encrypt string from stdin (for CI/CD)
```bash
echo -n 'supersecret123' | ansible-vault encrypt_string --stdin-name 'vault_api_key'
```

## Decrypting Secrets

### Decrypt file
```bash
ansible-vault decrypt group_vars/all/vault.yml
```

### View encrypted file without decrypting
```bash
ansible-vault view group_vars/all/vault.yml
```

### Decrypt string (not directly supported — use view or edit)
Use `ansible-vault view` on the file containing the encrypted string.

## Using Vault in Playbooks

### Provide password interactively
```bash
ansible-playbook playbook.yml --ask-vault-pass
```

### Provide password from file
```bash
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass
```

**~/.vault_pass**:
```
my_secure_vault_password
```

Set permissions:
```bash
chmod 600 ~/.vault_pass
```

### Provide password from script
```bash
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass.sh
```

**~/.vault_pass.sh** (executable):
```bash
#!/bin/bash
echo "$VAULT_PASSWORD"
```

Set permissions:
```bash
chmod 700 ~/.vault_pass.sh
```

### Configure in ansible.cfg
```ini
[defaults]
vault_password_file = ~/.vault_pass
```

## Multiple Vault Passwords (Vault IDs)

Use vault IDs to manage different passwords for different environments:

```bash
ansible-vault create --vault-id prod@prompt group_vars/production/vault.yml
ansible-vault create --vault-id staging@prompt group_vars/staging/vault.yml
```

Run playbook with multiple vault IDs:
```bash
ansible-playbook playbook.yml \
  --vault-id prod@~/.vault_pass_prod \
  --vault-id staging@~/.vault_pass_staging
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Ansible playbook
  env:
    VAULT_PASSWORD: ${{ secrets.ANSIBLE_VAULT_PASSWORD }}
  run: |
    echo "$VAULT_PASSWORD" > /tmp/vault_pass
    ansible-playbook playbook.yml --vault-password-file /tmp/vault_pass
    rm /tmp/vault_pass
```

### GitLab CI
```yaml
deploy:
  script:
    - echo "$VAULT_PASSWORD" > /tmp/vault_pass
    - ansible-playbook playbook.yml --vault-password-file /tmp/vault_pass
    - rm /tmp/vault_pass
  variables:
    VAULT_PASSWORD: $ANSIBLE_VAULT_PASSWORD  # set in GitLab CI/CD settings
```

### Jenkins
```groovy
withCredentials([string(credentialsId: 'ansible-vault-password', variable: 'VAULT_PASS')]) {
    sh '''
        echo "$VAULT_PASS" > /tmp/vault_pass
        ansible-playbook playbook.yml --vault-password-file /tmp/vault_pass
        rm /tmp/vault_pass
    '''
}
```

## External Secret Managers (Alternative to Vault)

For dynamic secrets or centralized secret management, use external tools:

### HashiCorp Vault
```yaml
- name: Fetch secret from Vault
  ansible.builtin.set_fact:
    db_password: "{{ lookup('hashi_vault', 'secret=secret/data/db:password') }}"
```

Requires `hvac` Python library and Vault token/auth.

### AWS Secrets Manager
```yaml
- name: Fetch secret from AWS
  ansible.builtin.set_fact:
    api_key: "{{ lookup('aws_secret', 'prod/api_key', region='us-east-1') }}"
```

Requires `boto3` and AWS credentials.

### Azure Key Vault
```yaml
- name: Fetch secret from Azure
  ansible.builtin.set_fact:
    db_password: "{{ lookup('azure_keyvault_secret', 'db-password', vault_url='https://myvault.vault.azure.net') }}"
```

Requires `azure-keyvault-secrets` and Azure authentication.

## Best Practices

### 1. Never commit unencrypted secrets
```bash
# Add to .gitignore
**/vault_pass*
**/.vault_pass*
```

### 2. Use separate vault files
Keep `vars.yml` (plain) and `vault.yml` (encrypted) separate for easier diffs.

### 3. Prefix vault variables
```yaml
# vault.yml
vault_db_password: "secret"
vault_api_key: "secret"

# vars.yml
db_password: "{{ vault_db_password }}"
api_key: "{{ vault_api_key }}"
```

### 4. Rotate vault passwords regularly
```bash
ansible-vault rekey group_vars/all/vault.yml
```

### 5. Use vault IDs for multi-environment projects
```bash
ansible-vault create --vault-id prod@prompt group_vars/production/vault.yml
ansible-vault create --vault-id dev@prompt group_vars/development/vault.yml
```

### 6. Never use `no_log: false` on tasks with secrets
```yaml
# ✅ Correct – secrets are hidden
- name: Create database user
  community.postgresql.postgresql_user:
    name: app_user
    password: "{{ vault_db_password }}"
  no_log: true

# ❌ Wrong – password will be logged
- name: Create database user
  community.postgresql.postgresql_user:
    name: app_user
    password: "{{ vault_db_password }}"
```

### 7. Validate vault files after editing
```bash
ansible-vault view group_vars/all/vault.yml
ansible-playbook playbook.yml --syntax-check --ask-vault-pass
```

## Common Issues

### "Decryption failed"
- Wrong vault password
- File corrupted (check with `ansible-vault view`)
- Multiple vault IDs — provide all required passwords

### "Vault format unhexlify error"
- File was manually edited while encrypted
- Re-encrypt from backup or recreate

### "ERROR! Attempting to decrypt but no vault secrets found"
- Missing `--vault-password-file` or `--ask-vault-pass`
- `vault_password_file` not set in `ansible.cfg`

## Quick Reference

| Command | Description |
|---|---|
| `ansible-vault create <file>` | Create new encrypted file |
| `ansible-vault encrypt <file>` | Encrypt existing file |
| `ansible-vault decrypt <file>` | Decrypt file (writes plain text) |
| `ansible-vault edit <file>` | Edit encrypted file in-place |
| `ansible-vault view <file>` | View encrypted file without decrypting |
| `ansible-vault rekey <file>` | Change vault password |
| `ansible-vault encrypt_string` | Encrypt single string for inline use |

---
**Remember:** Vault is for **static secrets**. For dynamic secrets, credential rotation, or centralized management, use external secret managers (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault).

Docs: https://docs.ansible.com/ansible/latest/vault_guide/index.html
