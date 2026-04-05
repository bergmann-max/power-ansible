#!/usr/bin/env python3
"""
Ansible Kiro Power – MCP Server
Provides tools to create, lint, and check Ansible playbooks and roles.
IMPORTANT: Only stderr for logs, stdout is reserved for JSON-RPC.
"""
import os, sys, subprocess, textwrap, configparser
from pathlib import Path
from mcp.server.fastmcp import FastMCP

PROJECT_ROOT = Path(os.getenv("ANSIBLE_PROJECT_ROOT", os.getcwd()))

def _resolve_inventory() -> Path | None:
    """Resolve inventory path in order of precedence."""
    # 1. Explicit env var
    if env := os.getenv("ANSIBLE_INVENTORY"):
        return Path(env)

    # 2. ansible.cfg [defaults] inventory
    cfg_path = PROJECT_ROOT / "ansible.cfg"
    if cfg_path.exists():
        cfg = configparser.ConfigParser()
        cfg.read(cfg_path)
        if cfg.has_option("defaults", "inventory"):
            raw = cfg.get("defaults", "inventory").strip()
            resolved = (PROJECT_ROOT / raw).resolve()
            if resolved.exists():
                return resolved

    # 3. Common fallback locations
    for candidate in ["hosts.yml", "hosts.ini", "inventory/hosts.yml", "inventory/hosts.ini"]:
        p = PROJECT_ROOT / candidate
        if p.exists():
            return p

    return None

INVENTORY = _resolve_inventory()

mcp = FastMCP("ansible-dev")

# ── Helpers ──────────────────────────────────────────────────────────────────

def _write(path: Path, content: str) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content))
    return {"ok": True, "path": str(path)}

def _run(cmd: list[str]) -> dict:
    try:
        r = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60)
        return {"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e)}

def _require_inventory() -> tuple[Path | None, dict | None]:
    """Returns (inventory_path, error_dict). If error_dict is set, return it immediately."""
    if INVENTORY is None:
        return None, {
            "ok": False,
            "error": (
                "No inventory found. Provide one via:\n"
                "  1. ANSIBLE_INVENTORY env var\n"
                "  2. ansible.cfg [defaults] inventory\n"
                "  3. hosts.yml or hosts.ini in project root"
            )
        }
    return INVENTORY, None

# ── Scaffold Tools ────────────────────────────────────────────────────────────

@mcp.tool()
def create_playbook(name: str, hosts: str, description: str = "", become: bool = False) -> dict:
    """Creates a new Ansible playbook with correct structure and FQCN comments.

    Args:
        name:        File name without extension, e.g. 'deploy_webserver'
        hosts:       Target hosts/group, e.g. 'webservers' or 'all'
        description: Short description of the playbook
        become:      Whether sudo/root is required (default: False)
    """
    become_str = "true" if become else "false"
    content = f"""\
        ---
        # {description or name}
        # Run:     ansible-playbook -i inventory/hosts.ini playbooks/{name}.yml
        # Dry-Run: ansible-playbook --check -i inventory/hosts.ini playbooks/{name}.yml

        - name: {description or name}
          hosts: {hosts}
          gather_facts: true
          become: {become_str}
          tags:
            - {name.replace('_', '-')}

          vars:
            # Define variables here or move them to group_vars/
            # example_var: "value"

          pre_tasks:
            - name: Ensure prerequisites
              ansible.builtin.assert:
                that:
                  - ansible_os_family is defined
                fail_msg: "Fact gathering failed – check SSH connectivity"
              tags: always

          tasks:
            - name: Example task – print hello
              ansible.builtin.debug:
                msg: "Hello from {{{{ inventory_hostname }}}}"
              tags:
                - debug

          handlers:
            - name: restart example service
              ansible.builtin.service:
                name: example
                state: restarted
        """
    path = PROJECT_ROOT / "playbooks" / f"{name}.yml"
    return _write(path, content)


@mcp.tool()
def create_role(role_name: str, description: str = "") -> dict:
    """Creates a complete Ansible role directory structure.

    Args:
        role_name:   Name of the role, e.g. 'nginx' or 'common'
        description: Short description of the role
    """
    base = PROJECT_ROOT / "roles" / role_name
    files = {
        "tasks/main.yml": f"""\
            ---
            # Tasks for role: {role_name}
            # {description}

            - name: Include OS-specific tasks
              ansible.builtin.include_tasks: "{{{{ ansible_os_family | lower }}}}.yml"
              when: ansible_os_family is defined
              tags: always

            - name: Example task
              ansible.builtin.debug:
                msg: "Role {role_name} is running on {{{{ inventory_hostname }}}}"
              tags:
                - {role_name}
            """,
        "handlers/main.yml": f"""\
            ---
            # Handlers for role: {role_name}

            - name: restart {role_name}
              ansible.builtin.service:
                name: {role_name}
                state: restarted
              listen: "restart {role_name}"
            """,
        "defaults/main.yml": f"""\
            ---
            # Default variables (lowest precedence, easy to override)
            # for role: {role_name}

            {role_name}_enabled: true
            {role_name}_version: "latest"
            """,
        "vars/main.yml": f"""\
            ---
            # Internal variables (high precedence, not meant to be overridden externally)
            # for role: {role_name}

            _{role_name}_supported_os:
              - RedHat
              - Debian
            """,
        "meta/main.yml": f"""\
            ---
            galaxy_info:
              role_name: {role_name}
              author: "your_name"
              description: "{description or role_name}"
              license: "MIT"
              min_ansible_version: "2.18"
              platforms:
                - name: EL
                  versions:
                    - "8"
                    - "9"
                - name: Ubuntu
                  versions:
                    - jammy
                    - noble
              galaxy_tags: []

            dependencies: []
            """,
        "templates/.gitkeep": "",
        "files/.gitkeep": "",
        "README.md": f"""\
            # Role: {role_name}

            {description or "Add description here."}

            ## Requirements

            - Ansible >= 2.18

            ## Variables

            | Variable | Default | Description |
            |---|---|---|
            | `{role_name}_enabled` | `true` | Enable/disable the role |
            | `{role_name}_version` | `"latest"` | Version |

            ## Example Playbook

            ```yaml
            - hosts: servers
              roles:
                - role: {role_name}
                  vars:
                    {role_name}_enabled: true
            ```
            """,
    }
    created = []
    for rel, content in files.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(content))
        created.append(str(p.relative_to(PROJECT_ROOT)))
    return {"ok": True, "role": role_name, "files_created": created}


@mcp.tool()
def scaffold_inventory(groups: list[str] = None, hosts: list[str] = None) -> dict:
    """Creates an inventory structure with hosts.ini and group_vars/.

    Args:
        groups: List of host groups, e.g. ['webservers', 'dbservers']
        hosts:  List of hosts, e.g. ['web01.example.com', 'db01.example.com']
    """
    groups = groups or ["webservers", "dbservers"]
    hosts  = hosts  or ["host1.example.com", "host2.example.com"]

    ini_lines = ["[all]"]
    for h in hosts:
        ini_lines.append(h)
    ini_lines.append("")
    for g in groups:
        ini_lines.append(f"[{g}]")
        ini_lines.append(f"# add hosts here")
        ini_lines.append("")

    ini_path = PROJECT_ROOT / "inventory" / "hosts.ini"
    _write(ini_path, "\n".join(ini_lines))

    all_vars = """\
        ---
        # Variables for all hosts
        ansible_user: "{{ lookup('env', 'ANSIBLE_USER') | default('ansible') }}"
        ansible_python_interpreter: /usr/bin/python3
        """
    _write(PROJECT_ROOT / "inventory" / "group_vars" / "all.yml", all_vars)

    for g in groups:
        _write(PROJECT_ROOT / "inventory" / "group_vars" / f"{g}.yml",
               f"---\n# Variables for group: {g}\n")

    return {"ok": True, "inventory": str(ini_path), "groups": groups}


@mcp.tool()
def create_ansible_cfg() -> dict:
    """Creates an ansible.cfg with sensible default values."""
    content = """\
        [defaults]
        inventory          = inventory/hosts.ini
        roles_path         = roles
        collections_path   = collections
        host_key_checking  = False
        retry_files_enabled = False
        stdout_callback    = yaml
        callbacks_enabled  = profile_tasks
        interpreter_python = auto_silent

        [privilege_escalation]
        become       = False
        become_method = sudo
        become_ask_pass = False

        [ssh_connection]
        pipelining    = True
        ssh_args      = -o ControlMaster=auto -o ControlPersist=60s
        """
    return _write(PROJECT_ROOT / "ansible.cfg", content)


# ── Validation Tools ──────────────────────────────────────────────────────────

@mcp.tool()
def lint_file(path: str) -> dict:
    """Runs ansible-lint on a file or directory.

    Args:
        path: Relative path to the file or role directory.
    """
    return _run(["ansible-lint", "--profile", "production", path])


@mcp.tool()
def syntax_check(playbook: str) -> dict:
    """Checks the syntax of a playbook without executing it.

    Args:
        playbook: Relative path to the playbook.
    """
    inv, err = _require_inventory()
    if err:
        return err
    return _run(["ansible-playbook", "--syntax-check", "-i", str(inv), playbook])


@mcp.tool()
def diff_check(playbook: str, limit: str = None) -> dict:
    """Runs a playbook in check+diff mode to preview what would change without making any changes.

    Args:
        playbook: Relative path to the playbook.
        limit:    Optional host limit, e.g. 'webservers' or 'web01.example.com'
    """
    inv, err = _require_inventory()
    if err:
        return err
    cmd = ["ansible-playbook", "--check", "--diff", "-i", str(inv), playbook]
    if limit:
        cmd.extend(["--limit", limit])
    return _run(cmd)


@mcp.tool()
def gather_facts(host: str) -> dict:
    """Collects all Ansible facts from a host using the setup module.

    Args:
        host: Hostname or group from the inventory, e.g. 'web01.example.com' or 'webservers'
    """
    inv, err = _require_inventory()
    if err:
        return err
    return _run(["ansible", "-i", str(inv), host, "-m", "setup"])


# ── List Tools ────────────────────────────────────────────────────────────────

@mcp.tool()
def list_playbooks() -> dict:
    """Lists all playbooks in the project."""
    p = PROJECT_ROOT / "playbooks"
    if not p.exists():
        return {"ok": True, "playbooks": []}
    return {"ok": True, "playbooks": sorted(str(f.relative_to(PROJECT_ROOT)) for f in p.rglob("*.yml"))}


@mcp.tool()
def list_roles() -> dict:
    """Lists all local roles in the project."""
    r = PROJECT_ROOT / "roles"
    if not r.exists():
        return {"ok": True, "roles": []}
    return {"ok": True, "roles": sorted(d.name for d in r.iterdir() if d.is_dir())}


@mcp.tool()
def show_role_tree(role_name: str) -> dict:
    """Shows the file structure of a role.

    Args:
        role_name: Name of the role.
    """
    base = PROJECT_ROOT / "roles" / role_name
    if not base.exists():
        return {"ok": False, "error": f"Role '{role_name}' not found"}
    files = sorted(str(f.relative_to(PROJECT_ROOT)) for f in base.rglob("*") if f.is_file())
    return {"ok": True, "role": role_name, "files": files}


# ── Entry Point ───────────────────────────────────────────────────────────────
def main():
    print(f"[ansible-power] PROJECT_ROOT={PROJECT_ROOT}", file=sys.stderr)
    print(f"[ansible-power] INVENTORY={INVENTORY or 'not found'}", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
