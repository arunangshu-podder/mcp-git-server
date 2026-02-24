# Using MCP Git Server with Copilot in VS Code

This guide explains how to use the MCP Git Server as a Model Context Protocol (MCP) server for GitHub Copilot in VS Code.

## Prerequisites

- VS Code with GitHub Copilot extension installed
- Python 3.7+ with Flask
- Git configured on your system
- The MCP Git Server running locally

## Setup Instructions

### 1. Start the Flask HTTP Server (in Terminal 1)

First, run the main git HTTP server in the background:

```bash
cd /Users/arunangshupodder/mcp-git-server
python run_server.py --host 127.0.0.1 --port 5000
```

Output should show:
```
 * Running on http://127.0.0.1:5000
```

### 2. Configure Copilot in VS Code (in VS Code Settings)

#### Option A: Using settings.json (Recommended)

1. Open **VS Code Settings** (`Cmd+,` on macOS)
2. Search for `modelContextProtocol` or go to **Settings > Extensions > GitHub Copilot**
3. Open `settings.json` (click "Edit in settings.json")
4. Add or update the MCP server configuration:

```json
{
  "modelContextProtocol": {
    "servers": {
      "git": {
        "command": "python3",
        "args": ["-m", "mcp_git_server.mcp_server"],
        "cwd": "${workspaceFolder}"
      }
    }
  }
}
```

5. Save and reload VS Code (`Cmd+Shift+P` → "Reload Window")

#### Option B: Using .copilot-settings.json (Workspace)

If you have a `.copilot-settings.json` in your workspace root (already created in this project):

```bash
cat .copilot-settings.json
```

Copilot will automatically detect and load this configuration.

### 3. Verify MCP Server Connection

After restarting VS Code:
1. Open the **Copilot** chat panel (`Cmd+Shift+L` or `Cmd+I`)
2. Check the Copilot output panel for logs
3. Try asking Copilot: *"What git operations are available?"*

Expected response: Copilot should list available tools (git_clone, git_status, git_pull, etc.).

## Available MCP Tools

Once connected, Copilot can invoke these git tools:

| Tool | Description |
|------|-------------|
| `git_clone` | Clone a repository |
| `git_status` | Get repository status |
| `git_pull` | Pull from remote (supports `--rebase`) |
| `git_push` | Push to remote with specified branch |
| `git_commit` | Commit staged changes |
| `git_add` | Add files to staging area |
| `git_checkout` | Checkout a branch (with create option) |
| `git_branch` | Get current branch name |
| `git_log` | Show recent commits |
| `git_fetch` | Fetch from remote |

## Usage Examples with Copilot

### Example 1: Clone a Repository
```
User: "Clone the repo https://github.com/example/repo.git to ~/projects"

Copilot will use git_clone with:
{
  "repo_url": "https://github.com/example/repo.git",
  "dest": "~/projects"
}
```

### Example 2: Check Repository Status
```
User: "What's the status of the project at ~/my-repo?"

Copilot will use git_status with:
{
  "repo_path": "~/my-repo",
  "human": true
}
```

### Example 3: Pull with Rebase
```
User: "Pull the latest changes from origin main with rebase"

Copilot will use git_pull with:
{
  "repo_path": "~/my-repo",
  "remote": "origin",
  "branch": "main",
  "rebase": true
}
```

### Example 4: Commit and Push
```
User: "Add all changes and commit with message 'feat: add new feature', then push to origin"

Copilot will sequence:
1. git_add: {"repo_path": "~/my-repo", "paths": "."}
2. git_commit: {"repo_path": "~/my-repo", "message": "feat: add new feature"}
3. git_push: {"repo_path": "~/my-repo", "remote": "origin", "branch": "main"}
```

## Environment Variables (Token Auth)

If you need GitHub/Azure DevOps token authentication:

```bash
# For GitHub
export GITHUB_TOKEN=your_github_token

# For Azure DevOps
export ADO_PAT=your_ado_pat

# Then start the server
python run_server.py --host 127.0.0.1 --port 5000
```

Or configure in `config.yml`:
```yaml
auth:
  github_token: ${GITHUB_TOKEN}
  ado_pat: ${ADO_PAT}
```

## Troubleshooting

### MCP Server Not Found
- Ensure the Flask server is running on `http://127.0.0.1:5000`
- Check the configured `cwd` points to the correct project directory
- Verify Python path: `which python3` should match your configured command

### Connection Refused
```bash
# Check if Flask server is running:
lsof -i :5000

# If not, start it:
python run_server.py --host 127.0.0.1 --port 5000
```

### Token Authentication Issues
- Ensure environment variables are set before starting the server
- Tokens will be injected into HTTPS URLs temporarily during operations
- Original remote URLs are restored after operations complete

### Debugging
Check Copilot logs in VS Code:
- **View > Output > GitHub Copilot**
- Look for MCP server connection messages

## Architecture Overview

```
┌─────────────────────┐
│  Copilot (VS Code)  │
└──────────┬──────────┘
           │
           │ MCP Protocol (stdio)
           │
┌──────────▼──────────────────┐
│  MCP Git Server             │
│  (mcp_git_server.py)        │
└──────────┬──────────────────┘
           │
           │ HTTP requests
           │ (urllib)
           │
┌──────────▼──────────────────┐
│  Flask HTTP Server          │
│  (run_server.py)            │
│  - Port 5000                │
└──────────┬──────────────────┘
           │
           │ subprocess calls
           │
┌──────────▼──────────────────┐
│  Git CLI                    │
│  (/opt/homebrew/bin/git)    │
└─────────────────────────────┘
```

## Performance Notes

- **First tool invocation** may take 1-2 seconds (Python startup)
- **Subsequent calls** are fast (< 500ms) as the server stays warm
- **Large operations** (clone, fetch) may take longer depending on network/repo size
- Set `GIT_TIMEOUT` environment variable to adjust timeout (default: 30s)

## Security Notes

1. **Local Only**: Flask server only binds to `127.0.0.1` by default (not accessible from network)
2. **Token Handling**: Tokens are injected temporarily and original URLs are restored after operations
3. **Input Validation**: All endpoints validate repo_path exists and reject invalid inputs
4. **Safe Mode**: `run_safe` endpoint blocks dangerous git commands

## Advanced Configuration

### Custom Git Path
Edit `config.yml`:
```yaml
git:
  path: /usr/bin/git  # or /opt/homebrew/bin/git on macOS
```

### Custom Timeout
```bash
export GIT_TIMEOUT=60
python run_server.py --host 127.0.0.1 --port 5000
```

### Running on Different Port
```bash
python run_server.py --host 127.0.0.1 --port 5001
# Then update settings.json to match
```

## Support

For issues, check:
1. Flask server logs (Terminal 1)
2. Copilot output panel in VS Code
3. `.git/config` for proper remotes
4. Environment variables for tokens

---

**Next Steps**: Start the Flask server and configure VS Code settings, then use Copilot naturally to invoke git operations!
