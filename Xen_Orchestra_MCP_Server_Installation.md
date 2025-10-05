# Section 2: Installation Instructions for the Xen Orchestra MCP Server

Follow these steps to set up and run your custom MCP server for Xen Orchestra. (Outdated)

---

## Step 1: Save the Files

```bash
# Create project directory
mkdir xen-orchestra-mcp-server
cd xen-orchestra-mcp-server

# Save all 5 files in this directory:
# - Dockerfile
# - requirements.txt
# - xen_orchestra_server.py
# - readme.txt
# - CLAUDE.md
```

---

## Step 2: Build Docker Image

```bash
docker build -t xen-orchestra-mcp-server .
```

---

## Step 3: Set Up Secrets (if needed)

```bash
# Only include if the server needs API keys or secrets
docker mcp secret set XO_API_TOKEN="your-secret-value"

# Verify secrets
docker mcp secret list
```

---

## Step 4: Create Custom Catalog

```bash
# Create catalogs directory if it doesn't exist
mkdir -p ~/.docker/mcp/catalogs

# Create or edit custom.yaml
vim ~/.docker/mcp/catalogs/custom.yaml
```

Add this entry to `custom.yaml`:

```yaml
version: 2
name: custom
displayName: Custom MCP Servers
registry:
  xen-orchestra:
    description: "MCP Server for managing Xen Orchestra VMs and backups"
    title: "Xen Orchestra"
    type: server
    dateAdded: "2025-10-04T00:00:00Z"
    image: xen-orchestra-mcp-server:latest
    ref: ""
    readme: ""
    toolsUrl: ""
    source: ""
    upstream: ""
    icon: ""
    tools:
      - name: list_vms
      - name: create_vm
      - name: delete_vm
      - name: modify_vm
      - name: list_backups
      - name: create_backup
      - name: delete_backup
    secrets:
      - name: XO_API_TOKEN
        env: XO_API_TOKEN
        example: "my-secret-api-token"
    metadata:
      category: automation
      tags:
        - xen orchestra
        - vm
        - backup
      license: MIT
      owner: local
```

---

## Step 5: Update Registry

```bash
# Edit registry file
vim ~/.docker/mcp/registry.yaml
```

Add this entry under the existing `registry:` key:

```yaml
registry:
  # ... existing servers ...
  xen-orchestra:
    ref: ""
```

⚠️ **Important:** The entry must be under the `registry:` key, not at the root level.

---

## Step 6: Configure Claude Desktop

Locate your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Edit the file and add your custom catalog to the args array:

```json
{
  "mcpServers": {
    "mcp-toolkit-gateway": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "[YOUR_HOME]/.docker/mcp:/mcp",
        "docker/mcp-gateway",
        "--catalog=/mcp/catalogs/docker-mcp.yaml",
        "--catalog=/mcp/catalogs/custom.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--tools-config=/mcp/tools.yaml",
        "--transport=stdio"
      ]
    }
  }
}
```

Replace `[YOUR_HOME]` with:

- **macOS**: `/Users/your_username`
- **Windows**: `C:\\Users\\your_username` (use double backslashes)
- **Linux**: `/home/your_username`

---

## Step 7: Restart Claude Desktop

1. Quit Claude Desktop completely  
2. Start Claude Desktop again  
3. Your new tools should appear!  

---

## Step 8: Test Your Server

```bash
# Verify it appears in the list
docker mcp server list

# If you don't see your server, check logs:
docker logs [container_name]
```

---
