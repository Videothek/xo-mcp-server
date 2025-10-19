#!/usr/bin/env python3
import logging
import sys
from mcp.server.fastmcp import FastMCP
from tools import vm, backup
from config import XO_BASE_URL, XO_API_TOKEN, logger


# ================= Initialize MCP Server =================
# Initializes the MCP server instance.
# The string is the server's name, which shows up in the client.
mcp = FastMCP("xo_mcp_server")


# ================= Register MCP Tools =================
# Register the MCP tools from the submodule.
# Each tool must be registered seperatly

# Register VM related functions as MCP tools.
mcp.list_vms = mcp.tool()(vm.list_vms)
mcp.create_vm = mcp.tool()(vm.create_vm)

#Register Backup related functions as MCP tools.
mcp.list_backups = mcp.tool()(backup.list_backups)


# ================= Server Startup =================
if __name__ == "__main__":

    logger.info("Starting Xen Orchestra MCP server...")

    if not XO_API_TOKEN.strip():
        logger.warning(f"XO_API_TOKEN not set. Some tools may fail. Token: {XO_API_TOKEN}")

    try:

        # Starts the MCP server using standard input/output transport.
        # You can change transport to 'tcp' or 'websocket' if needed.
        mcp.run(transport='stdio')

    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)

        # Exits the program if server fails.
        sys.exit(1)