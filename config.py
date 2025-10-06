import os
import sys
import logging
from datetime import datetime, timezone


# ================= Logging Configuration =================
# Central configuration for MCP Server and tools logging

# Read log level from environment variable, default to INFO
log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()

# Map string to logging level, fallback to INFO if invalid
log_level = getattr(logging, log_level_str, logging.INFO)


logging.basicConfig(
    level=log_level,  # Set logging level.
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Customize how logs appear.
    stream=sys.stderr  # Logs are sent to standard error.
)

# Creates a logger for the MCP server and tools.
logger = logging.getLogger("xo_mcp_server")


# ================= Xen Orchestra Configuration =================
# Place any constants, URLs, or secrets here.
# Example: XO API token from Docker secrets or environment variables

# Reads the Xen Orchestra API token from an environment variable.
XO_API_TOKEN = os.environ.get("XO_API_TOKEN", "")

# Base URL for your Xen Orchestra instance.
XO_BASE_URL = os.environ.get("XO_BASE_URL", "http://localhost:80")


# ================= SSL Configuration =================
# Configuration for SSL options of the httpx request.

# Certificate verify option for the Xen Orchestra webserver
CERT_VERIFY = os.environ.get("CERT_VERIFY", "True").lower() == "true"

# Certificate path to the self-signed certificate of the Xen ORchestra webserver
CERT_PATH = os.environ.get("CERT_PATH", None)

# Set the certificate verification parameter for the httpx requestes
httpx_verify = CERT_PATH if CERT_PATH else CERT_VERIFY