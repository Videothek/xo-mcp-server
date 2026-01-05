import urllib.parse
import httpx
from typing import Annotated
from pydantic import Field
from config import XO_BASE_URL, XO_API_TOKEN, httpx_verify, logger

# ================= DOCS MCP Tools =================
# Each MCP tool is a function decorated with @mcp.tool()
# It must return a string and have single-line docstrings.



# ================= Get Swagger Docs =================
# Get the swagger docs for the Xen Orchestra API
async def get_docs(
):

    # Tool description
    """
    Get the swagger documentation for the Xen Orchestra API.
    Use this tool to fetch information on how to use fields and filters for the other MCP Tool calls.

    """

    # Logging output
    logger.info("Fetching swagger docs from Xen Orchestra")

    try:
        # Set the Request headers
        headers = {
            "Accept": "application/json",
            "Cookie": f"authenticationToken={XO_API_TOKEN}"
        }

        # Build URL with Parameters
        url = f"{XO_BASE_URL}/rest/v0/docs/swagger.json"

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
                    "swagger-docs": data
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
        logger.error(f"Exception encountered while calling the Xen Orchestra URL: {e}")

        # Return an error code to the client if an exception was raised
        return {
                "status": "failure",
                "type": "exception",
                "error-text": str(e)
        }