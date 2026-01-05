# Section 2: Installation Instructions

Follow these steps to set up and run your custom MCP server for Xen Orchestra. (Outdated)

---

## Step 1: Clone repository

```bash
# Pull the repository
git clone https://github.com/Videothek/xo-mcp-server.git

# Move into the folder
cd xo-mcp-server

```

---

## Step 2: Build Docker Image

```bash
docker build -t xo-mcp-server .
```

---

## Step 3: Set up Docker MCP secrets

```bash
# Set the Xen Orchestra URL
docker mcp secret set XO_BASE_URL="http://example.lan"

# Set the Xen Orchestra API token
docker mcp secret set XO_API_TOKEN="your-secret-api-token"

# Set the SSL check variable
docker mcp secret set CERT_VERIFY="False"

# Set the SSL path (optional)
docker mcp secret set CERT_PATH="/path/to/your/ssl/cert.pem"

# Verify secrets
docker mcp secret ls
```

---

## Step 4: Create custom Docker MCP catalog


```bash
Linux:
# Create catalogs directory if it doesn't exist
mkdir -p ~/.docker/mcp/catalogs

# Create or edit custom.yaml
vim ~/.docker/mcp/catalogs/custom.yaml


Windows:
# Create catalogs directory if it doesn't exist
C:\Users\<windows-user>\.docker\mcp\catalogs
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
    image: xo-mcp-server:latest
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
      - name: XO_BASE_URL
        env: XO_BASE_URL
        example: "http://example.lan"
      - name: XO_API_TOKEN
        env: XO_API_TOKEN
        example: "your-secret-api-token"
      - name: CERT_VERIFY
        env: CERT_VERIFY
        example: "False"
      - name: CERT_PATH
        env: CERT_PATH
        example: ""
      
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

## Step 5: Update Docker MCP Registry

```bash
Linux:
# Edit registry file
vim ~/.docker/mcp/registry.yaml

Windows:
C:\Users\<windows-user>\.docker\mcp\registry.yaml
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

## Step 6: Configure Clients


### Continue VS-Code

Go to your Continue settings in VS Code:

```bash
Windows:
C:\Users\<windows-user>\.continue\config.yaml
```

Add the following to the buttom of the config file:

```bash
mcpServers:
  - name: MCP_DOCKER
    command: docker
    args:
      - mcp
      - gateway
      - run
      - --catalog="C:\Users\<windows-user>\.docker\mcp\catalogs\custom.yaml"
    env:
      LOCALAPPDATA: |-
        C:\Users\<windows-user>\AppData\Local
      ProgramData: C:\ProgramData
      ProgramFiles: C:\Program Files
```

 💡 **Please Note:** You can also let Docker Desktop configure Continue for you through the MCP Toolkit Clients section

After the configuration is added, Continue should be able to use the MCP Server through the Docker MCP Gateway.


### Claude Desktop (not tested)

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
- **Windows**: `C:\\Users\\windows-user` (use double backslashes)
- **Linux**: `/home/your_username`

---

Restart Claude Desktop

1. Quit Claude Desktop completely
2. Start Claude Desktop again
3. Your new tools should appear!

---

## Step 8: Check that the MCP server is working

```bash
# Verify that the xo-mcp-server appears in the list
docker mcp server list

# Verify that the Gateway can execute the container
docker mcp gateway run --dry-run
```

---
