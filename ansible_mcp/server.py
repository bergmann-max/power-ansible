#!/usr/bin/env python3
"""
Ansible Kiro Power – MCP Server
Provides tools to lint and validate Ansible playbooks and roles.
File creation is handled directly by the agent via its file tools.
IMPORTANT: Only stderr for logs, stdout is reserved for JSON-RPC.
"""
import os, subprocess, configparser
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ansible")

# ── Helpers ──────────────────────────────────────────────────────────────────

def _resolve_root(project_root: str) -> tuple[Path | None, dict | None]:
    """Validate and resolve project_root.

    Catches unresolved IDE variables like '${workspaceFolder}' and returns a
    clear error instead of silently operating in the wrong directory.
    """
    if not project_root:
        return None, {
            "ok": False,
            "error": "project_root is required. Pass the absolute path to the Ansible workspace."
        }
    if project_root.startswith("${") or project_root.startswith("$("):
        return None, {
            "ok": False,
            "error": (
                f"project_root contains an unresolved variable: {project_root!r}. "
                "Pass the actual absolute path, e.g. '/home/user/my-project'."
            )
        }
    p = Path(project_root)
    if not p.is_absolute():
        return None, {
            "ok": False,
            "error": f"project_root must be an absolute path, got: {project_root!r}"
        }
    if not p.exists():
        return None, {
            "ok": False,
            "error": f"project_root does not exist: {project_root!r}"
        }
    return p, None


def _resolve_inventory(root: Path) -> Path | None:
    """Resolve inventory path in order of precedence."""
    if env := os.getenv("ANSIBLE_INVENTORY"):
        return Path(env)
    cfg_path = root / "ansible.cfg"
    if cfg_path.exists():
        cfg = configparser.ConfigParser()
        cfg.read(cfg_path)
        if cfg.has_option("defaults", "inventory"):
            raw = cfg.get("defaults", "inventory").strip()
            resolved = (root / raw).resolve()
            if resolved.exists():
                return resolved
    for candidate in ["hosts.yml", "hosts.yaml", "hosts.ini",
                      "inventory/hosts.yml", "inventory/hosts.yaml", "inventory/hosts.ini"]:
        p = root / candidate
        if p.exists():
            return p
    return None


def _require_inventory(root: Path) -> tuple[Path | None, dict | None]:
    inv = _resolve_inventory(root)
    if inv is None:
        return None, {
            "ok": False,
            "error": (
                "No inventory found. Provide one via:\n"
                "  1. ANSIBLE_INVENTORY env var\n"
                "  2. ansible.cfg [defaults] inventory\n"
                "  3. hosts.yml or hosts.ini in project root"
            )
        }
    return inv, None


def _run(cmd: list[str], cwd: Path) -> dict:
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        return {"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    except Exception as e:
        return {"ok": False, "stdout": "", "stderr": str(e)}


# ── Validation Tools ──────────────────────────────────────────────────────────

@mcp.tool()
def lint_file(path: str, project_root: str) -> dict:
    """Runs ansible-lint on a file or directory.

    Args:
        path:         Absolute path to the file or role directory to lint.
        project_root: Absolute path to the Ansible project root (workspace folder).
    """
    root, err = _resolve_root(project_root)
    if err:
        return err
    return _run(["ansible-lint", "--profile", "production", path], cwd=root)


@mcp.tool()
def syntax_check(playbook: str, project_root: str) -> dict:
    """Checks the syntax of a playbook without executing it.

    Args:
        playbook:     Absolute path to the playbook file.
        project_root: Absolute path to the Ansible project root (workspace folder).
    """
    root, err = _resolve_root(project_root)
    if err:
        return err
    inv, err = _require_inventory(root)
    if err:
        return err
    return _run(["ansible-playbook", "--syntax-check", "-i", str(inv), playbook], cwd=root)


@mcp.tool()
def diff_check(playbook: str, project_root: str, limit: str = "") -> dict:
    """Runs a playbook in check+diff mode to preview changes without applying them.

    Args:
        playbook:     Absolute path to the playbook file.
        project_root: Absolute path to the Ansible project root (workspace folder).
        limit:        Optional host limit, e.g. 'webservers' or 'web01.example.com'
    """
    root, err = _resolve_root(project_root)
    if err:
        return err
    inv, err = _require_inventory(root)
    if err:
        return err
    cmd = ["ansible-playbook", "--check", "--diff", "-i", str(inv), playbook]
    if limit:
        cmd.extend(["--limit", limit])
    return _run(cmd, cwd=root)


@mcp.tool()
def gather_facts(host: str, project_root: str) -> dict:
    """Collects all Ansible facts from a host using the setup module.

    Args:
        host:         Hostname or group from the inventory.
        project_root: Absolute path to the Ansible project root (workspace folder).
    """
    root, err = _resolve_root(project_root)
    if err:
        return err
    inv, err = _require_inventory(root)
    if err:
        return err
    return _run(["ansible", "-i", str(inv), host, "-m", "setup"], cwd=root)


@mcp.tool()
def list_hosts(playbook: str, project_root: str, limit: str = "") -> dict:
    """Lists all hosts that would be affected by a playbook run.

    Args:
        playbook:     Absolute path to the playbook file.
        project_root: Absolute path to the Ansible project root (workspace folder).
        limit:        Optional host limit, e.g. 'webservers' or 'web01.example.com'
    """
    root, err = _resolve_root(project_root)
    if err:
        return err
    inv, err = _require_inventory(root)
    if err:
        return err
    cmd = ["ansible-playbook", "--list-hosts", "-i", str(inv), playbook]
    if limit:
        cmd.extend(["--limit", limit])
    return _run(cmd, cwd=root)


@mcp.tool()
def list_tags(playbook: str, project_root: str) -> dict:
    """Lists all tags defined in a playbook.

    Args:
        playbook:     Absolute path to the playbook file.
        project_root: Absolute path to the Ansible project root (workspace folder).
    """
    root, err = _resolve_root(project_root)
    if err:
        return err
    inv, err = _require_inventory(root)
    if err:
        return err
    return _run(["ansible-playbook", "--list-tags", "-i", str(inv), playbook], cwd=root)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
