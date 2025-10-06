import logging
import urllib.parse
import httpx
from config import XO_BASE_URL, API_TOKEN, httpx_verify, logger

# ================= VM MCP Tools =================
# Each MCP tool is a function decorated with @mcp.tool()
# It must return a string and have single-line docstrings.


# ================= List VMs =================
# List all VMs with fields depending on filters
async def list_vms(fields: list[str] | None = None, filter: dict[str, str] | None = None, limit: int = 42):

    # Tool description
    """
    List all VMs in Xen Orchestra, with dynamic fields and filter.

    Parameters:
        fields: Optional[List[str]]
            The fields to include in the API response. Example: ["name_label", "name_description", "power_state", "uuid", "tags", "os_version"]
        filter: Optional[Dict[str, str]]
            Key-value filters, e.g. {"power_state": "Running", "container": "Ares", "tags": "Critical"}.
        limit: Optional[int]
            Max number of results (default: 42).

    Returns:
        dict: {
          "status": "success" or "failure",
          "total": <number of VMs>,
          "vms": [<VM objects>]
        }

    Returns on MCP Server failure:
        dict: {
          "status": "failure",
          "type": "http-error" or "exception",
          "status-code": "<http-status-code>",
          "error-texts": "<error-text>"
        }
    """

    # Logging output
    logger.info("Fetching VMs from Xen Orchestra")

    try:
        # Set the Request headers
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Accept": "application/json"
        }

        # Set defaults if client didn't provide any
        if not fields:
            fields = ["name_label", "name_description", "power_state", "uuid"]
        if not filter:
            filter = {"power_state": "Running"}

        # Prepare URL Parameters
        fields_param = urllib.parse.quote(",".join(fields))
        filter_param = urllib.parse.quote(" ".join(f"{k}:{v}" for k, v in filter.items()))

        # Build URL with Parameters
        url = f"{XO_BASE_URL}/rest/v0/vms?fields={fields_param}&filter={filter_param}&limit={limit}"

        # Output the URL for debugging
        logger.debug(f"Request URL: {url}")

        # Call the Xen Orchestra REST-API
        async with httpx.AsyncClient(verify=httpx_verify, timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Return MCP friendly list of information
            return {
                    "status": "success" if data.get("data") else "failure",
                    "total": len(data.get("data", [])),
                    "vms": data.get("data", [])
            }

    
    # Error handling for http request failures
    except httpx.HTTPStatusError as e:

        # Log an error code if the http request fails
        logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")

        # Return an error code to the client if the http request fails
        return {
                "status": "failure",
                "type": "http-error",
                "status-code":  e.response.status_code,
                "error-text": e.response.text
        }
    
    
    # Error handling for exceptions
    except Exception as e:

        # Log an error code if an exception was raised
        logger.error(f"Error listing VMs: {e}")

        # Return an error code to the client if an exception was raised
        return {
                "status": "failure",
                "type": "exception",
                "error-text": str(e)
        }


# ================= Create VM =================
# Create a VM from a template
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


# ================= Delete VM =================
# Delete a VM based on the id
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