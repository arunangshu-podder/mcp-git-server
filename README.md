# mcp-git-server

Minimal MCP-style HTTP server to run common Git operations via HTTP API and Model Context Protocol (MCP) for VS Code Copilot.

## Features

- 🔧 **12 Git Operations**: Clone, status, pull, push, commit, add, checkout, branch, log, fetch, merge, stash
- 🤖 **MCP Integration**: Works seamlessly with VS Code Copilot
- 🔐 **Automatic Token Authentication**: GitHub and Azure DevOps tokens injected automatically
- 🌐 **Cross-Platform**: macOS, Linux, and Windows support
- 🚫 **No Credential Prompts**: All git credential dialogs disabled
- ⏱️ **Configurable Timeouts**: Handle slow networks or large repositories

## Quick Start

1. **Install dependencies:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Configure tokens (optional):**

```bash
export GITHUB_TOKEN=ghp_your_github_token
export ADO_PAT=your_azure_devops_pat
```

3. **Run the server:**

```bash
python run_server.py --host 127.0.0.1 --port 5000
```

4. **Test the server:**

```bash
curl http://127.0.0.1:5000/api/health
```

## Available Tools

The server provides **12 git operations** accessible via MCP tools (for Copilot) or HTTP endpoints (for direct API calls):

| # | Tool | HTTP Endpoint | Description |
|---|------|---------------|-------------|
| 1 | `git_clone` | `POST /api/clone` | Clone a repository |
| 2 | `git_status` | `POST /api/status` | Get repository status |
| 3 | `git_pull` | `POST /api/pull` | Pull from remote (supports `--rebase`) |
| 4 | `git_push` | `POST /api/push` | Push to remote |
| 5 | `git_commit` | `POST /api/commit` | Commit staged changes |
| 6 | `git_add` | `POST /api/add` | Stage files for commit |
| 7 | `git_checkout` | `POST /api/checkout` | Switch or create branches |
| 8 | `git_branch` | `POST /api/branch` | Get current branch name |
| 9 | `git_log` | `POST /api/log` | Show commit history |
| 10 | `git_fetch` | `POST /api/fetch` | Fetch from remote |
| 11 | `git_merge` | `POST /api/merge` | Merge branches |
| 12 | `git_stash` | `POST /api/stash` | Manage stashes (save, list, apply, pop, drop, clear, show) |

**📖 For detailed parameters, examples, and usage, see [API_REFERENCE.md](API_REFERENCE.md)**

## Documentation

- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation with parameters, examples, and error handling
- **[MCP_SETUP.md](MCP_SETUP.md)** - VS Code Copilot integration guide
- **[TOKEN_AUTH_GUIDE.md](TOKEN_AUTH_GUIDE.md)** - Token authentication setup and troubleshooting
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide and common workflows
- **[WINDOWS_COMPATIBILITY.md](WINDOWS_COMPATIBILITY.md)** - Windows-specific setup instructions

## Example Usage

### Using Copilot (Natural Language)

```
"Clone https://github.com/torvalds/linux.git to ~/projects"
"What's the status of my repo at ~/my-project?"
"Pull the latest changes with rebase"
"Commit all changes with message 'feat: add login'"
"Push to origin main"
```

### Using HTTP API (Direct)

```bash
# Check status
curl -X POST http://127.0.0.1:5000/api/status \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/path/to/repo"}'

# Pull with rebase
curl -X POST http://127.0.0.1:5000/api/pull \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/path/to/repo","rebase":true}'

# Merge branch
curl -X POST http://127.0.0.1:5000/api/merge \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/path/to/repo","branch":"feature-branch"}'
```

See [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | - |
| `ADO_PAT` | Azure DevOps Personal Access Token | - |
| `GIT_TIMEOUT` | Operation timeout in seconds | `30` |
| `GIT_PATH` | Path to git executable | Auto-detected |
| `MCP_DEBUG` | Enable MCP debug logging | `0` |
| `GIT_RUNNER_DEBUG` | Enable git runner debug logging | `0` |

### Token Authentication

Tokens are automatically injected during remote operations (pull, push, fetch). Configure in `mcp.json` for Copilot:

```json
{
  "mcpServers": {
    "git": {
      "command": "python",
      "args": ["-m", "mcp_git_server.mcp_server"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token",
        "ADO_PAT": "your_ado_pat",
        "GIT_TIMEOUT": "240"
      }
    }
  }
}
```

See [TOKEN_AUTH_GUIDE.md](TOKEN_AUTH_GUIDE.md) for detailed setup instructions.

## License

MIT License - see LICENSE file for details.
