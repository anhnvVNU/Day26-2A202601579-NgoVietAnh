#!/usr/bin/env python3
"""
Verification script for Weather Agent setup
Checks if all components are configured correctly
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_environment():
    """Check if .env file exists and is configured"""
    print("🔍 Checking environment configuration...")
    
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: echo 'GOOGLE_API_KEY=your_key' > .env")
        return False
    
    # Check if GOOGLE_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        print("❌ GOOGLE_API_KEY not configured in .env")
        print("   Get key from: https://aistudio.google.com/apikey")
        return False
    
    print("✅ GOOGLE_API_KEY configured")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")

    from importlib.util import find_spec
    
    required_packages = [
        ("google.adk", "Google ADK"),
        ("mcp", "MCP"),
        ("dotenv", "python-dotenv"),
        ("httpx", "httpx"),
    ]
    
    all_installed = True
    for package, name in required_packages:
        try:
            installed = find_spec(package) is not None
        except (ImportError, ModuleNotFoundError):
            installed = False

        if installed:
            print(f"✅ {name}")
        else:
            print(f"❌ {name} not installed")
            all_installed = False
    
    if not all_installed:
        print("\n   Install with: uv sync")
    
    return all_installed

def check_agent_structure():
    """Check if agent directory structure is correct"""
    print("\n🔍 Checking agent structure...")
    
    required_files = [
        BASE_DIR / "weather_agent/agent.py",
        BASE_DIR / "weather_agent/__init__.py",
    ]
    
    all_exist = True
    for path in required_files:
        display_path = path.relative_to(BASE_DIR)
        if path.exists():
            print(f"✅ {display_path}")
        else:
            print(f"❌ {display_path} not found")
            all_exist = False
    
    return all_exist

def check_mcp_server():
    """Connect to the local MCP server and verify its advertised tools."""
    print("\n🔍 Checking MCP server connectivity...")
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")
    
    try:
        import asyncio
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client
        
        async def test_connection():
            async with streamablehttp_client(server_url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.list_tools()
                    health = await session.call_tool("health_check")
                    if health.isError:
                        raise RuntimeError("health_check tool returned an error")
                    return {tool.name for tool in result.tools}

        tools = asyncio.run(test_connection())
        expected = {"get_current_weather", "get_forecast", "health_check"}
        missing = expected - tools

        if not missing:
            print(f"✅ MCP server reachable at {server_url}")
            print(f"✅ All MCP tools discovered: {', '.join(sorted(expected))}")
            print("✅ health_check tool executed successfully")
            return True

        print(f"❌ Missing MCP tools: {', '.join(sorted(missing))}")
        return False
            
    except Exception as e:
        print(f"❌ Cannot reach MCP server: {e}")
        return False

def check_agent_import():
    """Try to import the agent"""
    print("\n🔍 Checking agent import...")
    
    try:
        # Suppress warnings during import
        import warnings
        warnings.filterwarnings("ignore")
        
        from weather_agent import root_agent
        print(f"✅ Agent imported successfully: {root_agent.name}")
        print(f"   Model: {root_agent.model}")
        return True
    except Exception as e:
        print(f"❌ Failed to import agent: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Weather Agent Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_environment(),
        check_dependencies(),
        check_agent_structure(),
        check_mcp_server(),
        check_agent_import(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ All checks passed!")
        print("\n🚀 Ready to start!")
        print("   Run: uv run adk web")
        print("\n📍 Then open: http://localhost:8000")
        return 0
    else:
        print("❌ Some checks failed")
        print("\n⚠️  Fix the issues above and run this script again")
        return 1

if __name__ == "__main__":
    sys.exit(main())

