#!/usr/bin/env python3
"""XenOrchMCP MCP Server - manage Xen Orchestra via REST API"""

import os
import sys
import logging
import json
from datetime import datetime, timezone
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("XenOrchMCP-server")

# Initialize MCP server - NO prompt parameter
mcp = FastMCP("XenOrchMCP")

# Configuration from environment variables
XOA_URL = os.environ.get("XOA_URL", "").rstrip("/")
XOA_TOKEN = os.environ.get("XOA_TOKEN", "")
DEFAULT_TIMEOUT = 15.0

# Utility: build base API URL
def _api_base() -> str:
    """Return the base REST API URL"""
    if not XOA_URL.strip():
        return ""
    return f"{XOA_URL}/rest/v0"

# Utility: create async client with cookie auth
def _client():
    """Create an httpx AsyncClient configured for Xen Orchestra"""
    cookies = {}
    if XOA_TOKEN.strip():
        cookies["authenticationToken"] = XOA_TOKEN.strip()
    headers = {"Accept": "application/json"}
    base = _api_base()
    if base:
        return httpx.AsyncClient(base_url=base, headers=headers, cookies=cookies, timeout=DEFAULT_TIMEOUT)
    return httpx.AsyncClient(headers=headers, cookies=cookies, timeout=DEFAULT_TIMEOUT)

# === MCP TOOLS ===

@mcp.tool()
async def list_vms(limit: str = "50", fields: str = "name_label,power_state") -> str:
    """List VMs with optional limit and fields"""
    logger.info("list_vms called")
    if not XOA_URL.strip() or not XOA_TOKEN.strip():
        return "❌ Error: XOA_URL and XOA_TOKEN environment variables must be set"
    try:
        limit_int = int(limit) if str(limit).strip() else 50
    except Exception:
        return f"❌ Error: Invalid limit value: {limit}"
    params = {}
    if str(fields).strip():
        params["fields"] = str(fields).strip()
    params["limit"] = str(limit_int)
    try:
        async with _client() as client:
            resp = await client.get("/vms", params=params)
            resp.raise_for_status()
            data = resp.json()
            # present a compact readable list
            out_lines = ["📊 VMs:"]
            if isinstance(data, list):
                for i, item in enumerate(data[:limit_int], start=1):
                    if isinstance(item, dict):
                        name = item.get("name_label", "<no name>")
                        state = item.get("power_state", "unknown")
                        href = item.get("href", "")
                        out_lines.append(f"- {i}. {name} (state: {state}) {href}")
                    else:
                        out_lines.append(f"- {i}. {item}")
            else:
                out_lines.append(f"⚠️ Unexpected response shape: {json.dumps(data)[:500]}")
            return "\n".join(out_lines)
    except httpx.HTTPStatusError as e:
        return f"❌ API Error: {e.response.status_code} - {e.response.text[:500]}"
    except Exception as e:
        logger.error("list_vms error", exc_info=True)
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def create_vm(payload: str = "") -> str:
    """Create a VM using JSON payload (POST /vms)"""
    logger.info("create_vm called")
    if not XOA_URL.strip() or not XOA_TOKEN.strip():
        return "❌ Error: XOA_URL and XOA_TOKEN environment variables must be set"
    if not str(payload).strip():
        return "❌ Error: payload is required and must be a JSON string"
    try:
        body = json.loads(payload)
    except Exception as e:
        return f"❌ Error: payload is not valid JSON: {str(e)}"
    try:
        async with _client() as client:
            resp = await client.post("/vms", json=body)
            resp.raise_for_status()
            data = resp.json()
            return f"✅ Success: VM creation request accepted\n- Response: {json.dumps(data)[:1000]}"
    except httpx.HTTPStatusError as e:
        return f"❌ API Error: {e.response.status_code} - {e.response.text[:1000]}"
    except Exception as e:
        logger.error("create_vm error", exc_info=True)
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def delete_vm(vm_id: str = "") -> str:
    """Delete a VM by its UUID or href"""
    logger.info("delete_vm called")
    if not XOA_URL.strip() or not XOA_TOKEN.strip():
        return "❌ Error: XOA_URL and XOA_TOKEN environment variables must be set"
    if not str(vm_id).strip():
        return "❌ Error: vm_id is required"
    vm_path = str(vm_id).strip()
    # If user passed full href, strip leading slash and /rest/v0 if present
    if vm_path.startswith("/rest/v0/"):
        vm_path = vm_path.replace("/rest/v0/", "")
    if vm_path.startswith("/"):
        vm_path = vm_path[1:]
    try:
        async with _client() as client:
            resp = await client.delete(f"/{vm_path}")
            if resp.status_code in (200, 204):
                return f"✅ Success: VM {vm_id} deleted (HTTP {resp.status_code})"
            else:
                # raise_for_status to provide details
                resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        return f"❌ API Error: {e.response.status_code} - {e.response.text[:1000]}"
    except Exception as e:
        logger.error("delete_vm error", exc_info=True)
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def modify_vm(vm_id: str = "", name_label: str = "", name_description: str = "") -> str:
    """Modify VM properties (name_label and/or name_description)"""
    logger.info("modify_vm called")
    if not XOA_URL.strip() or not XOA_TOKEN.strip():
        return "❌ Error: XOA_URL and XOA_TOKEN environment variables must be set"
    if not str(vm_id).strip():
        return "❌ Error: vm_id is required"
    payload = {}
    if str(name_label).strip():
        payload["name_label"] = str(name_label).strip()
    if str(name_description).strip():
        payload["name_description"] = str(name_description).strip()
    if not payload:
        return "❌ Error: At least one of name_label or name_description must be provided"
    vm_path = str(vm_id).strip()
    if vm_path.startswith("/rest/v0/"):
        vm_path = vm_path.replace("/rest/v0/", "")
    if vm_path.startswith("/"):
        vm_path = vm_path[1:]
    try:
        async with _client() as client:
            resp = await client.patch(f"/{vm_path}", json=payload)
            resp.raise_for_status()
            return f"✅ Success: VM updated\n- Updated fields: {', '.join(payload.keys())}"
    except httpx.HTTPStatusError as e:
        return f"❌ API Error: {e.response.status_code} - {e.response.text[:1000]}"
    except Exception as e:
        logger.error("modify_vm error", exc_info=True)
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def list_backup_jobs(job_type: str = "jobs") -> str:
    """List backup jobs (job_type controls path like 'jobs' or 'vm')"""
    logger.info("list_backup_jobs called")
    if not XOA_URL.strip() or not XOA_TOKEN.strip():
        return "❌ Error: XOA_URL and XOA_TOKEN environment variables must be set"
    jt = str(job_type).strip()
    # Known endpoints seen in docs/forums: /backup/jobs and /backup/jobs/vm
    path = "/backup"
    if jt:
        # safe join
        path = f"/backup/{jt}" if not jt.startswith("/") else f"/backup{jt}"
    try:
        async with _client() as client:
            resp = await client.get(path)
            resp.raise_for_status()
            data = resp.json()
            out_lines = [f"📊 Backup jobs at {path}:"]
            if isinstance(data, list):
                for i, j in enumerate(data, start=1):
                    if isinstance(j, dict):
                        name = j.get("name", j.get("name_label", "<no name>"))
                        jid = j.get("id", j.get("uuid", j.get("href", "")))
                        out_lines.append(f"- {i}. {name} (id: {jid})")
                    else:
                        out_lines.append(f"- {i}. {j}")
            else:
                out_lines.append(f"⚠️ Unexpected response shape: {json.dumps(data)[:500]}")
            return "\n".join(out_lines)
    except httpx.HTTPStatusError as e:
        return f"❌ API Error: {e.response.status_code} - {e.response.text[:1000]}"
    except Exception as e:
        logger.error("list_backup_jobs error", exc_info=True)
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def create_backup_job(payload: str = "") -> str:
    """Create a backup job using a JSON payload under /backup/jobs"""
    logger.info("create_backup_job called")
    if not XOA_URL.strip() or not XOA_TOKEN.strip():
        return "❌ Error: XOA_URL and XOA_TOKEN environment variables must be set"
    if not str(payload).strip():
        return "❌ Error: payload is required and must be a JSON string"
    try:
        body = json.loads(payload)
    except Exception as e:
        return f"❌ Error: payload is not valid JSON: {str(e)}"
    try:
        async with _client() as client:
            resp = await client.post("/backup/jobs", json=body)
            resp.raise_for_status()
            data = resp.json()
            return f"✅ Success: Backup job creation request accepted\n- Response: {json.dumps(data)[:1000]}"
    except httpx.HTTPStatusError as e:
        return f"❌ API Error: {e.response.status_code} - {e.response.text[:1000]}"
    except Exception as e:
        logger.error("create_backup_job error", exc_info=True)
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def delete_backup_job(job_id: str = "") -> str:
    """Delete a backup job by id or href"""
    logger.info("delete_backup_job called")
    if not XOA_URL.strip() or not XOA_TOKEN.strip():
        return "❌ Error: XOA_URL and XOA_TOKEN environment variables must be set"
    if not str(job_id).strip():
        return "❌ Error: job_id is required"
    jid = str(job_id).strip()
    if jid.startswith("/rest/v0/"):
        jid = jid.replace("/rest/v0/", "")
    if jid.startswith("/"):
        jid = jid[1:]
    # try to delete under backup/jobs/<id> as typical endpoint
    try:
        async with _client() as client:
            # if user provided full path, use it; otherwise try backup/jobs/<id> then /backup/<id>
            if "/" in jid and jid.startswith("backup"):
                resp = await client.delete(f"/{jid}")
            else:
                resp = await client.delete(f"/backup/jobs/{jid}")
            if resp.status_code in (200, 204):
                return f"✅ Success: Backup job {job_id} deleted (HTTP {resp.status_code})"
            else:
                resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        return f"❌ API Error: {e.response.status_code} - {e.response.text[:1000]}"
    except Exception as e:
        logger.error("delete_backup_job error", exc_info=True)
        return f"❌ Error: {str(e)}"

# Server startup
if __name__ == "__main__":
    logger.info("Starting XenOrchMCP MCP server...")
    if not XOA_URL.strip():
        logger.warning("XOA_URL not set; set XOA_URL to your Xen Orchestra base URL (no trailing slash)")
    if not XOA_TOKEN.strip():
        logger.warning("XOA_TOKEN not set; set XOA_TOKEN to an authentication token from Xen Orchestra UI")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
