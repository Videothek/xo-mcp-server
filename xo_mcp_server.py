#!/usr/bin/env python3

import os
import sys
import logging
from datetime import datetime, timezone
import httpx
# HTTP client library used to make requests to Xen Orchestra API. You can swap for requests or aiohttp if preferred.

from mcp.server.fastmcp import FastMCP

# ================= Logging Configuration =================
logging.basicConfig(
    level=logging.INFO,  # Set logging level. Change to DEBUG for verbose output.
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Customize how logs appear.
    stream=sys.stderr  # Logs are sent to standard error.
)
logger = logging.getLogger("xo_mcp_server")  # Creates a logger specifically for this server. You can change the name.

# ================= Initialize MCP Server =================
mcp = FastMCP("xo_mcp_server")
# Initializes the MCP server instance.
# The string is the server's name, which shows up in Claude Desktop.
# Do NOT add a 'prompt' parameter, it breaks MCP compliance.

# ================= Configuration =================
# Place any constants, URLs, or secrets here.
# Example: XO API token from Docker secrets or environment variables
API_TOKEN = os.environ.get("XO_API_TOKEN", "")
# Reads the Xen Orchestra API token from an environment variable.
# You can modify this line to read from a file, config, or secret manager.

XO_BASE_URL = os.environ.get("XO_BASE_URL", "http://localhost:80")
# Base URL for your Xen Orchestra instance.
# Change to match your Xen Orchestra hostname or IP.

# ================= Utility Functions =================
def format_response(success, message):
    """Helper function to consistently format MCP responses."""
    return f"✅ {message}" if success else f"❌ {message}"
# You can modify this to include more structured JSON or additional emojis.

# ================= MCP Tools =================
# Each MCP tool is a function decorated with @mcp.tool()
# It must return a string and have single-line docstrings.

@mcp.tool()
async def list_running_vms():
    """List all Running VMs in Xen Orchestra."""
    logger.info("Fetching VMs from Xen Orchestra")
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        # API authorization header. Change to 'Basic' if you use username/password auth.
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{XO_BASE_URL}/rest/v0/vms?fields=name_label%2Cpower_state%2Cuuid&filter=power_state%3ARunning&limit=42", headers=headers)
            # Sends GET request to the Xen Orchestra API endpoint for VMs.
            response.raise_for_status()  # Raises exception if status code >=400
            data = response.json()  # Converts response body to JSON
            # Format VM list into readable string
            vms = [f"- {vm.get('name_label', 'Unnamed')} ({vm.get('id')})" for vm in data.get('data', [])]
            return f"📊 VMs:\n" + "\n".join(vms) if vms else "📊 No VMs found."
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Error: {e.response.status_code}")
        return f"❌ HTTP Error: {e.response.status_code}"
    except Exception as e:
        logger.error(f"Error listing VMs: {e}")
        return f"❌ Error: {str(e)}"
# You can modify the endpoint or formatting here, e.g., add filters, sorting, or more fields.

@mcp.tool()
async def create_vm(name: str = "", template_id: str = ""):
    """Create a new VM from a template."""
    if not name.strip() or not template_id.strip():
        return "❌ Error: Both 'name' and 'template_id' are required"
    logger.info(f"Creating VM: {name} from template {template_id}")
    try:
        payload = {"name_label": name, "template": template_id}
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{XO_BASE_URL}/api/v1/vms", headers=headers, json=payload)
            response.raise_for_status()
            vm = response.json()
            return f"✅ VM created: {vm.get('name_label')} ({vm.get('id')})"
    except Exception as e:
        logger.error(f"Error creating VM: {e}")
        return f"❌ Error: {str(e)}"
# Modify payload to include CPU, RAM, or disk parameters as needed.

@mcp.tool()
async def delete_vm(vm_id: str = ""):
    """Delete a VM by its ID."""
    if not vm_id.strip():
        return "❌ Error: 'vm_id' is required"
    logger.info(f"Deleting VM: {vm_id}")
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.delete(f"{XO_BASE_URL}/api/v1/vms/{vm_id}", headers=headers)
            response.raise_for_status()
            return f"✅ VM {vm_id} deleted successfully"
    except Exception as e:
        logger.error(f"Error deleting VM: {e}")
        return f"❌ Error: {str(e)}"
# You could add a confirmation flag before deletion for safety.

@mcp.tool()
async def list_backups():
    """List all backup jobs."""
    logger.info("Fetching backups from Xen Orchestra")
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{XO_BASE_URL}rest/v0/backup-jobs?fields=name%2Cmode%2Ctype%2Cid&filter=type%3Abackup&limit=42", headers=headers)
            response.raise_for_status()
            data = response.json()
            backups = [f"- {b.get('name')} ({b.get('id')})" for b in data.get('data', [])]
            return f"📊 Backups:\n" + "\n".join(backups) if backups else "📊 No backup jobs found."
    except Exception as e:
        logger.error(f"Error listing backups: {e}")
        return f"❌ Error: {str(e)}"
# Modify this to include filters, schedules, or status fields.

# ================= Server Startup =================
if __name__ == "__main__":
    logger.info("Starting Xen Orchestra MCP server...")
    if not API_TOKEN.strip():
        logger.warning("XO_API_TOKEN not set. Some tools may fail.")

    try:
        mcp.run(transport='stdio')
        # Starts the MCP server using standard input/output transport.
        # You can change transport to 'tcp' or 'websocket' if needed.
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
# Exits the program if server fails.