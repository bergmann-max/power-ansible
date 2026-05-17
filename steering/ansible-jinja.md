# Ansible Jinja2 – Project Conventions

Full Jinja2 reference: <https://jinja.palletsprojects.com/en/stable/templates/>.
Ansible-specific filters/tests/lookups: <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/>.

## Hard rules in this project

1. **Quote every Jinja expression** — `"{{ var }}"`, not bare `{{ var }}` at
   value start. Lint: `jinja[invalid]`, `yaml[implicit-mapping]`.
2. **Spaces inside braces** — `{{ var }}`, never `{{var}}`. Lint:
   `jinja[spacing]`.
3. **No bare-variable `when:`** — `when: foo` fine; `when: "{{ foo }}"`
   not. Lint: `jinja[invalid]`, `no-jinja-when`.
4. **`default` / `mandatory` for optional vs. required vars** — see Defaults
   section for semantics, edge cases.
5. **`to_json` / `to_yaml` for structured content** — never implicit
   stringification (see `avoid-implicit` in `ansible-best-practices.md`).

## Variable expression vs. statement

```jinja
{{ expression }}   {# emits value into output         #}
{% statement %}    {# control flow, no output         #}
{# comment #}      {# stripped from rendered output   #}
```

## Defaults and required values

```yaml
# Optional with fallback
nginx_port: "{{ user_port | default(80) }}"

# Optional, fall back to another var
nginx_user: "{{ override_user | default(app_user) }}"

# Required — fail render if undefined
nginx_root: "{{ webroot | mandatory('webroot must be set') }}"

# Default only when var is undefined OR empty/false (second arg = true)
nginx_log_level: "{{ user_level | default('info', true) }}"
```

## Tests vs. filters

Tests use `is`; filters use `|`. Mix them = most common Jinja bug.

```yaml
# Tests — return bool
- when: my_var is defined
- when: my_var is not none
- when: my_list is iterable
- when: ansible_distribution is match('Ubuntu|Debian')
- when: result is succeeded
- when: result is changed
- when: result is failed
- when: result is skipped

# Filters — transform value
- "{{ my_list | length }}"
- "{{ my_string | upper }}"
- "{{ my_dict | combine(other_dict) }}"
```

## Non-obvious / project-mandated filters

Standard filters (`upper`, `trim`, `length`, `sort`, `replace`, `int`, `bool`,
`basename`, `regex_replace`, `b64encode`, `urlencode`, …): see Ansible builtin
docs above. Listed here: filters with project-specific semantics or
gotchas.

| Filter | Note |
|---|---|
| `mandatory('msg')` | fail render if var undefined — preferred over silent default |
| `password_hash('sha512', 'salt')` | crypt-style hash for `ansible.builtin.user` |
| `combine(other, recursive=true)` | deep merge dicts; without `recursive`, nested keys overwritten |
| `combine(other, list_merge='append')` | concat list values instead of replacing |
| `selectattr('k', 'eq', v)` / `rejectattr` | filter list-of-dicts by attr — see patterns below |
| `map(attribute='k')` | pluck attr from each dict; always `| list` after (see anti-patterns) |
| `dict2items` / `items2dict` | dict ↔ `[{key, value}, …]` — needed for looping dicts |
| `to_nice_yaml(indent=2)` / `to_nice_json(indent=2)` | structured emit — never implicit stringify |
| `from_json` / `from_yaml` | parse string back to structure |

```yaml
# Merge: later sources override earlier
merged_config: "{{ defaults | combine(env_config, user_config, recursive=true) }}"
```

## Whitespace control

Jinja inserts newline for every `{% ... %}` block. Use `-` on side to trim.
Critical for template files that must stay diff-clean.

```jinja
{# Standard — leaves blank lines #}
{% for vhost in nginx_vhosts %}
server {
  server_name {{ vhost.name }};
}
{% endfor %}

{# Trimmed — no extra blanks #}
{%- for vhost in nginx_vhosts %}
server {
  server_name {{ vhost.name }};
}
{%- endfor %}
```

For `templates/*.j2`, set in playbook or globally via `ansible.cfg`:

```ini
# ansible.cfg — trim/lstrip applied to ALL templates
[defaults]
jinja2_native = False
```

```yaml
# Per-task override
- ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: 'u=rw,g=r,o=r'
    trim_blocks: true      # default true
    lstrip_blocks: true    # default false — turn on for cleaner output
```

## `selectattr` / `rejectattr` patterns

```yaml
vars:
  servers:
    - { name: web01, env: prod, port: 80 }
    - { name: web02, env: stg,  port: 80 }
    - { name: db01,  env: prod, port: 5432 }

  # All prod servers
  prod_servers: "{{ servers | selectattr('env', 'eq', 'prod') | list }}"

  # All names of prod servers
  prod_names: "{{ servers | selectattr('env', 'eq', 'prod') | map(attribute='name') | list }}"

  # All non-prod
  non_prod: "{{ servers | rejectattr('env', 'eq', 'prod') | list }}"

  # Has the 'port' attribute defined
  with_port: "{{ servers | selectattr('port', 'defined') | list }}"
```

## Loop / conditional reminders

`loop.index` 1-based, `loop.index0` 0-based, `loop.first` / `loop.last` / `loop.length`
available inside `{% for %}`. Full if/elif/else and ternary (`x if cond else y`)
behave as standard Jinja — see linked docs.

## Lookups vs. filters

| | Lookup (`lookup`/`query`) | Filter (`|`) |
|---|---|---|
| Runs on | controller | controller (during render) |
| Source | external (file, env, vault) | value piped in |
| Caching | re-evaluated each render | n/a |
| Example | `{{ lookup('env', 'HOME') }}` | `{{ my_path \| basename }}` |

```yaml
# Read file from controller
config: "{{ lookup('file', 'configs/app.conf') }}"

# Env var (returns '' if unset; use default)
ssh_user: "{{ lookup('env', 'DEPLOY_USER') | default('deploy', true) }}"

# Template a file (Jinja-render before reading)
rendered: "{{ lookup('template', 'configs/app.conf.j2') }}"

# Generate password (idempotent — file persists)
db_pw: "{{ lookup('password', '/tmp/db_pw chars=ascii_letters,digits length=24') }}"

# Many results — use query() (alias for lookup with wantlist=true)
hosts: "{{ query('inventory_hostnames', 'webservers') }}"
```

## Template header (mandatory for all `.j2` files)

```jinja
{# Managed by Ansible – role: {{ role_name | default('<playbook>') }} #}
{# Manual changes will be overwritten on the next Ansible run! #}
```

## Anti-patterns

### Bare variable as YAML value

```yaml
# BAD — YAML parses {{ var }} ambiguously, triggers jinja[invalid]
listen: {{ port }}

# GOOD
listen: "{{ port }}"
```

### `when:` with Jinja delimiters

```yaml
# BAD — when: already evaluates Jinja, double-render wrong
- ansible.builtin.debug: { msg: hi }
  when: "{{ enabled }}"

# GOOD
- ansible.builtin.debug: { msg: hi }
  when: enabled | bool
```

### Implicit truthiness on strings

```yaml
# BAD — "false" (string) is truthy in Jinja
- when: my_var

# GOOD — explicit cast
- when: my_var | bool
```

### Comparing fact strings without normalizing

```yaml
# BAD — fragile: distro casing changes between releases
- when: ansible_distribution == "ubuntu"

# GOOD
- when: ansible_distribution | lower == 'ubuntu'

# BETTER — version-aware
- when: ansible_distribution == 'Ubuntu' and ansible_distribution_major_version | int >= 22
```

### `default()` swallowing legitimate falsy values

```yaml
# BAD — default fires when user passes 0 or '' or false
nginx_workers: "{{ user_workers | default(4) }}"

# GOOD — only fire when undefined
nginx_workers: "{{ user_workers if user_workers is defined else 4 }}"
```

### Forgetting `| list` after `map`/`select`/`selectattr`

`map`/`select`/`selectattr` return generators in Jinja2. Without `| list`,
`length` and re-iteration give wrong results.

```yaml
# BAD — generator, length always 0 after first iteration
names: "{{ servers | map(attribute='name') }}"

# GOOD
names: "{{ servers | map(attribute='name') | list }}"
```

## Debugging templates

```yaml
- ansible.builtin.debug: { var: my_complex_var }
- ansible.builtin.debug: { msg: "{{ servers | selectattr('env','eq','prod') | list }}" }
```

Render template locally without running playbook:
```bash
ansible localhost -m template -a "src=templates/nginx.conf.j2 dest=/tmp/out.conf" \
  -e @group_vars/all.yml
```