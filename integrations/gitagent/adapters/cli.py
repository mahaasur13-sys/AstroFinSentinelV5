"""GitAgent CLI — export-agent, import-agent, MCP, commit commands for MASFactory.

ATOM-GITAGENT-003: Phase 3 completion
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integrations.gitagent.adapters.gitagent_adapter import (
    GitAgentManifest,
    MASFactoryToGitAgentAdapter,
    load_gitagent_as_masfactory,
)

# Default 4 key agents for AstroFin
DEFAULT_AGENTS = [
    "AstroCouncil",
    "FundamentalAgent",
    "QuantAgent",
    "MacroAgent",
    "AstroCouncil",  # Synthesis is the orchestrator
]


def build_astrofin_topology(agent_names: list):
    """Build a MASFactory Topology from agent names."""
    from mas_factory.topology import Connection, Role, Topology

    # Import actual agent classes
    try:
        from agents._impl.astro_council import AstroCouncilAgent
        from agents._impl.fundamental_agent import FundamentalAgent
        from agents._impl.macro_agent import MacroAgent
        from agents._impl.quant_agent import QuantAgent
        from agents._impl.synthesis_agent import SynthesisAgent
    except ImportError:
        pass

    roles = []
    connections = []

    weight_map = {
        "AstroCouncil": 0.20,
        "FundamentalAgent": 0.12,
        "QuantAgent": 0.10,
        "MacroAgent": 0.08,
        "SynthesisAgent": 0.0,  # orchestrator
    }

    for name in agent_names:
        role = Role(
            name=name,
            agent_type=name,
            weight=weight_map.get(name, 0.1),
            capabilities=[f"analyze_{name.lower()}"],
            inputs=["market_state"],
            outputs=["signal"],
            timeout_ms=30000,
        )
        roles.append(role)

    # Connect all to synthesis
    for name in agent_names:
        if name != "SynthesisAgent":
            connections.append(Connection(from_node=name, to_node="SynthesisAgent"))

    # Input router
    connections.append(Connection(from_node="input", to_node="SynthesisAgent"))
    # Exit
    connections.append(Connection(from_node="SynthesisAgent", to_node="end"))

    topology = Topology(
        intention="AstroFin Sentinel V5 Multi-Agent Analysis",
        symbol="BTCUSDT",
        timeframe="SWING",
        version="5.0",
        roles=roles,
        connections=connections,
        entry_point="input",
        exit_point="end",
        metadata={
            "description": "AstroFin Sentinel V5 with KARL-AMRE loop and GitAgent export",
            "author": "AstroFin Team",
            "exported_from": "MASFactory",
        },
    )
    return topology


# ─── CLI Commands ─────────────────────────────────────────────────────────────


def cmd_export_agent(args):
    """Export a MASFactory agent/Topology to GitAgent package."""
    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()

    try:
        from mas_factory.engine import ProductionMASEngine
        from mas_factory.topology import Connection, Role, Topology
    except ImportError as e:
        print(f"ERROR: Failed to import MASFactory: {e}")
        return 1

    topology = build_astrofin_topology(args.agents)
    adapter = MASFactoryToGitAgentAdapter(args.package_name, str(output_dir))
    pkg_path = adapter.from_topology(topology)

    print(f"✅ Exported {len(args.agents)} agents to GitAgent package:")
    for agent in args.agents:
        print(f"   - {agent}")
    print(f"   Package: {pkg_path}")
    return 0


def cmd_import_agent(args):
    """Import a GitAgent package as MASFactory engine."""
    pkg_path = Path(args.package_path)
    if not pkg_path.exists():
        print(f"ERROR: Package path does not exist: {pkg_path}")
        return 1

    engine = load_gitagent_as_masfactory(str(pkg_path))
    if engine is None:
        print(f"❌ Failed to load GitAgent package: {pkg_path}")
        print("   (MASFactory may not be available)")
        return 1

    manifest = GitAgentManifest.from_yaml(pkg_path / "agent.yaml")
    print(f"✅ Loaded GitAgent package: {manifest.name}")
    print(f"   Version: {manifest.version}")
    print(f"   Description: {manifest.description}")
    print(f"   Sub-agents: {len(manifest.sub_agents or [])}")
    return 0


def cmd_roundtrip(args):
    """Test round-trip: export → import → verify."""
    import tempfile

    output_dir = Path(tempfile.mkdtemp())
    package_name = args.package_name or "test_roundtrip"

    # Export
    try:
        topology = build_astrofin_topology(
            args.agents if args.agents else DEFAULT_AGENTS
        )
        adapter = MASFactoryToGitAgentAdapter(package_name, str(output_dir))
        pkg_path = adapter.from_topology(topology)
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 1

    # Import
    engine = load_gitagent_as_masfactory(str(pkg_path))
    if engine is None:
        print("❌ Import failed")
        return 1

    manifest = GitAgentManifest.from_yaml(pkg_path / "agent.yaml")
    original_roles = set(args.agents if args.agents else DEFAULT_AGENTS)
    imported_roles = set(manifest.sub_agents or [])

    if original_roles == imported_roles:
        print("✅ Round-trip PASSED")
        print(f"   Original: {sorted(original_roles)}")
        print(f"   Imported: {sorted(imported_roles)}")
        return 0
    else:
        print("❌ Round-trip FAILED: mismatch")
        print(f"   Original: {sorted(original_roles)}")
        print(f"   Imported: {sorted(imported_roles)}")
        return 1


# ─── MCP Commands ──────────────────────────────────────────────────────────────


def cmd_mcp_search(args):
    """Search for MCP tools in Smithery / GitHub registry."""
    try:
        from integrations.gitagent.adapters.mcp_adapter import mcp_search
    except ImportError as e:
        print(f"ERROR: Failed to import MCP adapter: {e}")
        return 1

    print(f"🔍 Searching MCP tools for: '{args.query}'")
    print("-" * 60)

    tools = mcp_search(args.query, max_results=args.max_results)
    if not tools:
        print("No tools found. Try a different query.")
        return 0

    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   ID: {tool.tool_id}")
        print(f"   Source: {tool.source}")
        print(f"   Description: {tool.description[:100]}")
        if tool.stars:
            print(f"   Stars: {tool.stars}")
        print()
    return 0


def cmd_mcp_install(args):
    """Install an MCP tool."""
    try:
        from integrations.gitagent.adapters.mcp_adapter import mcp_install
    except ImportError as e:
        print(f"ERROR: Failed to import MCP adapter: {e}")
        return 1

    print(f"📦 Installing MCP tool: {args.tool_id}")
    result = mcp_install(args.tool_id, args.install_path)
    status = result["status"]

    if status == "already_installed":
        print(f"ℹ️  {result['message']}")
    elif status == "installed":
        print(f"✅ Installed: {result['tool']['name']}")
        print(f"   Tool ID: {result['tool_id']}")
        print(f"   Path: {result['install_path']}")
    else:
        print(f"❌ Install failed: {result}")
        return 1
    return 0


def cmd_mcp_list(args):
    """List installed MCP tools."""
    try:
        from integrations.gitagent.adapters.mcp_adapter import mcp_list
    except ImportError as e:
        print(f"ERROR: Failed to import MCP adapter: {e}")
        return 1

    tools = mcp_list(show_all=args.all)
    if not tools:
        print("No MCP tools found.")
        return 0

    for tool in tools:
        if tool.get("type") == "info":
            print(f"ℹ️  {tool['message']}")
        elif tool.get("type") == "divider":
            print(f"\n{tool['label']}")
        else:
            installed = tool.get("installed", False)
            mark = "✅" if installed else "○"
            print(f"{mark} {tool['name']} ({tool['tool_id']})")
            if installed:
                print(f"   Installed: {tool.get('local_path', 'unknown')}")
    return 0


def cmd_mcp_remove(args):
    """Remove an installed MCP tool."""
    try:
        from integrations.gitagent.adapters.mcp_adapter import mcp_remove
    except ImportError as e:
        print(f"ERROR: Failed to import MCP adapter: {e}")
        return 1

    result = mcp_remove(args.tool_id)
    if result["status"] == "removed":
        print(f"✅ Removed: {result['name']} ({result['tool_id']})")
    else:
        print(f"❌ Not found: {args.tool_id}")
        return 1
    return 0


# ─── Commit Commands ───────────────────────────────────────────────────────────


def cmd_commit(args):
    """Generate and optionally commit changes."""
    try:
        from integrations.gitagent.commit_generator import (
            generate_commit_message,
            preview_commit,
        )
    except ImportError as e:
        print(f"ERROR: Failed to import commit generator: {e}")
        return 1

    if args.preview:
        preview_commit(ref=args.ref)
        return 0

    msg = generate_commit_message(ref=args.ref)
    print("=" * 60)
    print("GENERATED COMMIT MESSAGE")
    print("=" * 60)
    print(msg.to_string())
    print("=" * 60)
    print(f"KARL Confidence Score: {msg.kar_score:.0%}")
    print(f"Reasoning: {msg.reasoning}")

    if args.execute:
        print("\n🔄 Executing git commit...")
        try:
            import subprocess

            result = subprocess.run(
                ["git", "commit", "-m", msg.to_string()],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("✅ Commit successful!")
                print(result.stdout)
            else:
                print("❌ Commit failed:")
                print(result.stderr)
                return 1
        except Exception as e:
            print(f"❌ Git error: {e}")
            return 1

    return 0


# ─── Validate Command ──────────────────────────────────────────────────────────


def cmd_validate(args):
    """Validate a GitAgent package."""
    pkg_path = Path(args.package_path)
    if not pkg_path.exists():
        print(f"ERROR: Package path does not exist: {pkg_path}")
        return 1

    manifest_path = pkg_path / "agent.yaml"
    if not manifest_path.exists():
        print("❌ Missing: agent.yaml")
        return 1

    try:
        manifest = GitAgentManifest.from_yaml(manifest_path)
    except Exception as e:
        print(f"❌ Invalid agent.yaml: {e}")
        return 1

    # Check required files
    required = ["SOUL.md", "RULES.md", "DUTIES.md"]
    missing = []
    for fname in required:
        if not (pkg_path / fname).exists():
            missing.append(fname)

    print(f"✅ Package: {manifest.name}")
    print(f"   Version: {manifest.version}")
    print(f"   Description: {manifest.description}")
    print(f"   Sub-agents: {len(manifest.sub_agents or [])}")

    if missing:
        print(f"\n⚠️  Missing files: {', '.join(missing)}")
    else:
        print("\n✅ All required files present")

    return 0


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="GitAgent CLI for MASFactory (AstroFin Sentinel V5)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # export-agent
    export_parser = subparsers.add_parser(
        "export-agent", help="Export MASFactory agents to GitAgent"
    )
    export_parser.add_argument("agents", nargs="+", help="Agent names to export")
    export_parser.add_argument(
        "--package-name", "-n", default="astrofin_agents", help="Package name"
    )
    export_parser.add_argument("--output-dir", "-o", help="Output directory")
    export_parser.set_defaults(func=cmd_export_agent)

    # import-agent
    import_parser = subparsers.add_parser(
        "import-agent", help="Import GitAgent package to MASFactory"
    )
    import_parser.add_argument("package_path", help="Path to GitAgent package")
    import_parser.set_defaults(func=cmd_import_agent)

    # roundtrip
    roundtrip_parser = subparsers.add_parser(
        "roundtrip", help="Test export → import → verify"
    )
    roundtrip_parser.add_argument(
        "--package-name", "-n", default="test_roundtrip", help="Package name"
    )
    roundtrip_parser.add_argument(
        "--agents", nargs="+", help="Agent names (default: 4 key agents)"
    )
    roundtrip_parser.set_defaults(func=cmd_roundtrip)

    # mcp-search
    mcp_search_parser = subparsers.add_parser(
        "mcp-search", help="Search MCP tools in Smithery/GitHub"
    )
    mcp_search_parser.add_argument("query", help="Search query")
    mcp_search_parser.add_argument(
        "--max-results", "-m", type=int, default=10, help="Max results"
    )
    mcp_search_parser.set_defaults(func=cmd_mcp_search)

    # mcp-install
    mcp_install_parser = subparsers.add_parser(
        "mcp-install", help="Install an MCP tool"
    )
    mcp_install_parser.add_argument("tool_id", help="Tool ID")
    mcp_install_parser.add_argument("--install-path", help="Custom install directory")
    mcp_install_parser.set_defaults(func=cmd_mcp_install)

    # mcp-list
    mcp_list_parser = subparsers.add_parser("mcp-list", help="List installed MCP tools")
    mcp_list_parser.add_argument(
        "--all", "-a", action="store_true", help="Show all available"
    )
    mcp_list_parser.set_defaults(func=cmd_mcp_list)

    # mcp-remove
    mcp_remove_parser = subparsers.add_parser(
        "mcp-remove", help="Remove an installed MCP tool"
    )
    mcp_remove_parser.add_argument("tool_id", help="Tool ID to remove")
    mcp_remove_parser.set_defaults(func=cmd_mcp_remove)

    # commit
    commit_parser = subparsers.add_parser("commit", help="Generate commit message")
    commit_parser.add_argument("--ref", help="Git ref to diff against")
    commit_parser.add_argument(
        "--preview", "-p", action="store_true", help="Preview only"
    )
    commit_parser.add_argument(
        "--execute", "-e", action="store_true", help="Execute git commit"
    )
    commit_parser.set_defaults(func=cmd_commit)

    # validate
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a GitAgent package"
    )
    validate_parser.add_argument("package_path", help="Path to GitAgent package")
    validate_parser.set_defaults(func=cmd_validate)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
