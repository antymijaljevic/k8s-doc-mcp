# Python MPC Server Sample

A simple sticky notes application built with the MCP (Model Context Protocol) Python SDK.

## Features

- Add sticky notes
- Read all saved notes
- Get the latest note
- Generate note summaries

## Installation

1. Install the `uv` package manager:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Initialize the project and install dependencies:
   ```bash
   uv init .
   uv add "mcp[cli]"
   ```

3. Install the MCP server:
   ```bash
   uv run mcp install main.py
   ```

## Usage

Start the MCP server:
```bash
uv run python main.py
```

This will add json defintion to Claude Desktop (to MPC Host/Client) like this and run server in background.
```json
{
  "mcpServers": {
    "AI Sticky Notes": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "~/my-repositories/my-projects/python-mpc-server-sample/main.py"
      ]
    }
  }
}
```

### Available Functions

- `add_note(message)`: Add a new note
- `read_notes()`: Read all saved notes
- `get_latest_note()`: Get the most recent note
- `note_summary_prompt()`: Generate a prompt for summarizing notes

## Resources

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [uv Package Manager](https://docs.astral.sh/uv/getting-started/installation/)