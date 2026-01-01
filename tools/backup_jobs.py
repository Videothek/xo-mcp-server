import urllib.parse
import httpx
from typing import Annotated
from pydantic import Field
from config import XO_BASE_URL, XO_API_TOKEN, httpx_verify, logger

# ================= Backup MCP Tools =================
# Each MCP tool is a function decorated with @mcp.tool()
# It must return a string and have single-line docstrings.



# ================= List Backup Jobs =================
# List all backup jobs with their {fields} depending on {filters}
async def list_backup_jobs(
    fields: Annotated[list[str], Field(description="The fields for the backup jobs to include in the API response")] = None,
    filter: Annotated[dict[str, str], Field(description="Key-value filters to filter for backup job types")] = None,
    limit: Annotated[int, Field(description="Max number of results (default: 42)")] = 42
):

    # Tool description
    """
    List all backup jobs in Xen Orchestra, use filters and fields to customize the output.
    Check the documentation of the API for infos on how to use the arguments: https://docs.xcp-ng.org/management/manage-at-scale/xo-api/

    fields:
        - "name": backup job name
        - "mode": backup mode
        - "type": backup job type
        - "id":   backup job id
    filter:
        - "type": Filter for backup job types [backup, metadataBackup, call]
        - "mode": Filter for the backup mode [full, delta]
    limit: Maximum number of results to return. Set to 999 to return all VMs.
    """

    # Logging output
    logger.info("Fetching backup jobs from Xen Orchestra")

    try:
        # Set the Request headers
        headers = {
            "Accept": "application/json",
            "Cookie": f"authenticationToken={XO_API_TOKEN}"
        }

        # Set defaults if client didn't provide any
        if not fields:
            fields = ["name", "mode", "type", "id"]

        # Prepare URL Parameters
        fields_param = urllib.parse.quote(",".join(fields))
        filter_param = urllib.parse.quote(" ".join(f"{k}:{v}" for k, v in filter.items()))

        # Build URL with Parameters
        url = f"{XO_BASE_URL}/rest/v0/backup-jobs?fields={fields_param}&filter={filter_param}&limit={limit}"

        # Output the URL for debugging
        logger.debug(f"Request URL: {url}")

        # Call the Xen Orchestra REST-API
        async with httpx.AsyncClient(verify=httpx_verify, timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            #Remove the href to not confuse the client
            for item in data:
                item.pop("href", None)

            # Return MCP friendly list of information
            return {
                    "status": "success" if data else "failure",
                    "total": len(data),
                    "backup-jobs": data
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
        logger.error(f"Exception encountered while fetching the Xen Orchestra URL: {e}")

        # Return an error code to the client if an exception was raised
        return {
                "status": "failure",
                "type": "exception",
                "error-text": str(e)
        }



# ================= Get Backup Job Details =================
# List details for a backup job
async def get_backup_job_details(
    id: Annotated[str, Field(description="The id of the backup job to list details for, use list_backup_jobs to get the id")] = None
):

    # Tool description
    """
    Provide more details for a backup job in Xen Orchestra, use filters and fields to customize the output.
    Check the documentation of the API for infos on how to use the arguments: https://docs.xcp-ng.org/management/manage-at-scale/xo-api/

    id: Mandatory, use the list_backup_jobs tool before to retrieve the id of the backup job.
    """

    # Logging output
    logger.info("Fetching backup job details from Xen Orchestra")

    try:
        # Set the Request headers
        headers = {
            "Accept": "application/json",
            "Cookie": f"authenticationToken={XO_API_TOKEN}"
        }

        # Build URL with Parameters
        url = f"{XO_BASE_URL}/rest/v0/backup-jobs/{id}"

        # Output the URL for debugging
        logger.debug(f"Request URL: {url}")

        # Call the Xen Orchestra REST-API
        async with httpx.AsyncClient(verify=httpx_verify, timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Return MCP friendly list of information
            return {
                    "status": "success" if data else "failure",
                    "backup-job-details": data
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
        logger.error(f"Exception encountered while fetching the Xen Orchestra URL: {e}")

        # Return an error code to the client if an exception was raised
        return {
                "status": "failure",
                "type": "exception",
                "error-text": str(e)
        }