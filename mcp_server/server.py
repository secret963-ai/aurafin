"""
AuraFin MCP Server
Standalone FastMCP server exposing 4 core tools.
Run: python mcp_server/server.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from tools.mcp_tools import (
    check_installment_status,
    generate_referral_token,
    query_job_market,
    activate_escrow_contract,
)

mcp = FastMCP("AuraFin MCP Server")
mcp.tool()(check_installment_status)
mcp.tool()(generate_referral_token)
mcp.tool()(query_job_market)
mcp.tool()(activate_escrow_contract)

if __name__ == "__main__":
    print("AuraFin MCP Server starting...")
    mcp.run(transport="stdio")
