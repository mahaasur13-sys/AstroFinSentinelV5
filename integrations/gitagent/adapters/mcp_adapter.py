"""integrations/gitagent/adapters/mcp_adapter.py — ATOM-GITAGENT-003: MCP Adapter

MCP (Model Context Protocol) integration for Smithery / GitHub MCP registry.
Provides discovery, installation, and wrapper for MCP tools as MASFactory agents.
"""

import json
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

CACHE_DIR = Path.home() / ".cache" / "astrofin" / "mcp_tools"
MCP_REGISTRY_URL = "https://smithery.ai/api/v1/tools"
GITHUB_MCP_URL = (
    "https://api.github.com/search/repositories?q=mcp-server+in:name+topic:mcp"
)


@dataclass
class MCPTool:
    """Represents an MCP tool."""

    tool_id: str
    name: str
    description: str
    category: str = "general"
    source: str = "smithery"  # smithery | github | local
    install_command: Optional[str] = None
    homepage: Optional[str] = None
    stars: int = 0
    verified: bool = False
    local_path: Optional[str] = None
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["installed"] = self.is_installed()
        return d

    def is_installed(self) -> bool:
        if self.local_path:
            return Path(self.local_path).exists()
        return False


@dataclass
class MCPConfig:
    """MCP configuration for a workspace."""

    installed_tools: Dict[str, MCPTool] = field(default_factory=dict)
    config_path: Path = field(
        default_factory=lambda: Path.home() / ".config" / "astrofin" / "mcp.json"
    )

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "tools": {k: v.to_dict() for k, v in self.installed_tools.items()},
        }
        self.config_path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls) -> "MCPConfig":
        cfg = cls()
        if cfg.config_path.exists():
            try:
                data = json.loads(cfg.config_path.read_text())
                for k, v in data.get("tools", {}).items():
                    v.pop("installed", None)
                    cfg.installed_tools[k] = MCPTool(**v)
            except (json.JSONDecodeError, TypeError):
                pass
        return cfg


def _http_get(url: str, timeout: int = 10) -> Optional[Dict]:
    """Make HTTP GET request with timeout."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "AstroFin-Sentinel/5.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        json.JSONDecodeError,
        TimeoutError,
    ):
        return None


def mcp_search(query: str, max_results: int = 10) -> List[MCPTool]:
    """
    Search for MCP tools in Smithery registry.

    Args:
        query: Search query (e.g., "financial data", "trading", "crypto")
        max_results: Maximum number of results

    Returns:
        List of MCPTool objects
    """
    tools: List[MCPTool] = []

    # Search Smithery
    try:
        search_url = f"{MCP_REGISTRY_URL}?q={query}&limit={max_results}"
        data = _http_get(search_url)
        if data and isinstance(data, dict):
            results = data.get("tools", []) or data.get("results", []) or []
            for item in results[:max_results]:
                if isinstance(item, dict):
                    tools.append(
                        MCPTool(
                            tool_id=item.get("id", item.get("tool_id", "")),
                            name=item.get("name", "unknown"),
                            description=item.get("description", ""),
                            category=item.get("category", "general"),
                            source="smithery",
                            install_command=item.get(
                                "installCommand", item.get("install_command")
                            ),
                            homepage=item.get("homepage", item.get("url")),
                        )
                    )
    except Exception:
        pass

    # Search GitHub MCP topics
    try:
        github_url = f"https://api.github.com/search/repositories?q=mcp+{query.replace(' ', '+')}+in:name&sort=stars&order=desc&per_page={max_results}"
        data = _http_get(github_url)
        if data and isinstance(data, dict):
            for item in (data.get("items", []) or [])[:max_results]:
                if isinstance(item, dict):
                    tool_id = f"github:{item.get('full_name', '')}"
                    existing = next((t for t in tools if t.tool_id == tool_id), None)
                    if not existing:
                        tools.append(
                            MCPTool(
                                tool_id=tool_id,
                                name=item.get("name", ""),
                                description=item.get("description", "") or "",
                                category="github",
                                source="github",
                                homepage=item.get("html_url"),
                                stars=item.get("stargazers_count", 0),
                                verified=item.get("stargazers_count", 0) > 100,
                            )
                        )
    except Exception:
        pass

    return tools[:max_results]


def mcp_install(tool_id: str, install_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Install an MCP tool and create a local wrapper.

    Args:
        tool_id: Tool identifier (smithery ID or github:owner/repo)
        install_path: Optional custom install directory

    Returns:
        Dict with status, message, and tool info
    """
    cfg = MCPConfig.load()

    # Check if already installed
    if tool_id in cfg.installed_tools:
        tool = cfg.installed_tools[tool_id]
        if tool.is_installed():
            return {
                "status": "already_installed",
                "tool_id": tool_id,
                "tool": tool.to_dict(),
                "message": f"Tool '{tool.name}' is already installed",
            }

    # Search for the tool
    name_part = tool_id.replace("github:", "").replace("smithery:", "")
    found = mcp_search(name_part, max_results=20)
    matched = next(
        (t for t in found if tool_id in (t.tool_id, f"github:{name_part}", name_part)),
        None,
    )

    if not matched:
        # Create a placeholder entry
        matched = MCPTool(
            tool_id=tool_id,
            name=name_part,
            description=f"MCP tool: {name_part}",
            source="local",
        )

    # Determine install location
    base = Path(install_path) if install_path else CACHE_DIR
    base.mkdir(parents=True, exist_ok=True)
    safe_name = tool_id.replace("/", "_").replace(":", "_")
    tool_dir = base / safe_name
    tool_dir.mkdir(parents=True, exist_ok=True)

    # Write wrapper script
    wrapper_script = f'''#!/usr/bin/env python3
"""MCP Tool wrapper: {matched.name}"""
import subprocess
import sys

TOOL_ID = "{tool_id}"
TOOL_NAME = "{matched.name}"

def run_tool(*args):
    """Run MCP tool command."""
    cmd = ["mcp", "run", TOOL_ID] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run_tool(*sys.argv[1:]))
    else:
        print(f"MCP Tool: {{TOOL_NAME}} (ID: {{TOOL_ID}})")
'''
    wrapper_path = tool_dir / f"{safe_name}_wrapper.py"
    wrapper_path.write_text(wrapper_script)
    wrapper_path.chmod(0o755)

    # Write metadata
    meta_path = tool_dir / "meta.json"
    meta_path.write_text(json.dumps(matched.to_dict(), indent=2))

    # Update config
    matched.local_path = str(tool_dir)
    cfg.installed_tools[tool_id] = matched
    cfg.save()

    return {
        "status": "installed",
        "tool_id": tool_id,
        "tool": matched.to_dict(),
        "install_path": str(tool_dir),
        "wrapper": str(wrapper_path),
    }


def mcp_list(show_all: bool = False) -> List[Dict[str, Any]]:
    """
    List all available and installed MCP tools.

    Args:
        show_all: If True, show all known tools; if False, only installed

    Returns:
        List of tool dictionaries
    """
    cfg = MCPConfig.load()
    result = []

    if show_all:
        # Show installed tools
        for tool in cfg.installed_tools.values():
            result.append(tool.to_dict())
        result.append({"type": "divider", "label": "--- Installed tools ---"})
        # Show popular MCP servers from GitHub
        popular = mcp_search("trading finance crypto", max_results=15)
        for tool in popular:
            if tool.tool_id not in cfg.installed_tools:
                result.append({**tool.to_dict(), "installed": False})
    else:
        for tool in cfg.installed_tools.values():
            result.append(tool.to_dict())
        if not result:
            result.append(
                {
                    "type": "info",
                    "message": "No MCP tools installed. Run: python -m integrations.gitagent.cli mcp-search <query>",
                }
            )

    return result


def mcp_remove(tool_id: str) -> Dict[str, Any]:
    """Remove an installed MCP tool."""
    cfg = MCPConfig.load()

    if tool_id not in cfg.installed_tools:
        return {"status": "not_found", "tool_id": tool_id}

    tool = cfg.installed_tools[tool_id]
    tool_dir = (
        Path(tool.local_path)
        if tool.local_path
        else CACHE_DIR / tool_id.replace("/", "_")
    )

    if tool_dir.exists():
        import shutil

        shutil.rmtree(tool_dir)

    del cfg.installed_tools[tool_id]
    cfg.save()

    return {"status": "removed", "tool_id": tool_id, "name": tool.name}


def get_mcp_wrapper(tool_id: str) -> Optional[str]:
    """Get the path to a tool's wrapper script."""
    cfg = MCPConfig.load()
    if tool_id in cfg.installed_tools:
        tool = cfg.installed_tools[tool_id]
        if tool.local_path:
            safe_name = tool_id.replace("/", "_").replace(":", "_")
            return str(Path(tool.local_path) / f"{safe_name}_wrapper.py")
    return None
