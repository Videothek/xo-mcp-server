import logging
import urllib.parse
import httpx
from mcp import FastMCP
from config import XO_BASE_URL, API_TOKEN, httpx_verify, logger

# ================= Backup MCP Tools =================
# Each MCP tool is a function decorated with @mcp.tool()
# It must return a string and have single-line docstrings.



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