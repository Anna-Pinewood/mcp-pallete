

## MCP Config json

```json
{
  "mcpServers": {
    "mcp-pallete": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/mcp-pallete",
        "run",
        "src/app.py"
      ],
      "env": {
        "IMAGGA_API_KEY": "YOUR_IMAGGA_API_KEY",
        "IMAGGA_API_SECRET": "YOUR_IMAGGA_API_SECRET"
      }
    }
  }
}
```