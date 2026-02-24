# MCP Git Server - Quick Reference

## 🚀 Quick Start

### Terminal 1: Start the Flask Server
```bash
cd /Users/arunangshupodder/mcp-git-server
./start.sh
# or
python run_server.py --host 127.0.0.1 --port 5000
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
```

### VS Code: Configure Copilot

**Settings > Extensions > GitHub Copilot > settings.json:**

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

Then reload VS Code (`Cmd+Shift+P` → Reload Window)

---

## 💬 Chat with Copilot Examples

### Clone a Repo
```
"Clone https://github.com/octocat/Hello-World.git to ~/projects"
```

### Check Status
```
"Show me the status of my project at ~/SwagLabsDemoProject"
```

### Pull with Rebase
```
"Pull the latest from origin main and rebase my changes"
```

### Commit and Push
```
"Add all my changes, commit with 'feat: add login', and push to origin"
```

### Create and Checkout Branch
```
"Create a new branch called 'fix/issue-123' and checkout"
```

### View Commit History
```
"Show me the last 10 commits"
```

---

## 📋 Available Tools

| Tool | Git Command | Use Case |
|------|-------------|----------|
| `git_clone` | `git clone` | Clone repositories |
| `git_status` | `git status` | Check status |
| `git_add` | `git add` | Stage changes |
| `git_commit` | `git commit -m` | Commit changes |
| `git_push` | `git push origin main` | Push to remote |
| `git_pull` | `git pull [--rebase]` | Pull from remote |
| `git_checkout` | `git checkout -b` | Switch/create branches |
| `git_branch` | `git branch` | Show current branch |
| `git_log` | `git log` | View commit history |
| `git_fetch` | `git fetch` | Fetch from remote |

---

## 🔧 Configuration

### Token-Based Authentication

```bash
# GitHub
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Azure DevOps
export ADO_PAT=<pat_token>

# Then start the server
./start.sh
```

### Custom Port
```bash
./start.sh 127.0.0.1 5001
```

### Git Executable Path
Edit `config.yml`:
```yaml
git:
  path: /opt/homebrew/bin/git
```

---

## ✅ Health Check

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "git_path": "/opt/homebrew/bin/git"
}
```

---

## 🐛 Troubleshooting

### Server not starting
```bash
# Check if port 5000 is in use
lsof -i :5000

# If needed, use different port
./start.sh 127.0.0.1 5001
```

### Copilot not finding tools
1. Ensure Flask server is running (`ctrl+c` then restart)
2. Reload VS Code window (`Cmd+Shift+P` → "Reload Window")
3. Check Copilot output logs (`View > Output > GitHub Copilot`)

### Git command fails
- Verify repo path exists: `ls -la ~/path/to/repo`
- Check git config: `cd ~/repo && git remote -v`
- Check tokens are set (if using auth): `echo $GITHUB_TOKEN`

---

## 📚 Full Documentation

See [MCP_SETUP.md](./MCP_SETUP.md) for detailed setup, architecture, and troubleshooting.

---

## 🎯 Architecture

```
Copilot Chat → MCP Protocol → mcp_server.py → Flask Server → Git CLI
```

- **Copilot Chat**: Natural language requests in VS Code
- **MCP Protocol**: Standardized tool invocation (stdio)
- **mcp_server.py**: Tool adapter (lists tools, processes calls)
- **Flask Server**: HTTP endpoints for git operations
- **Git CLI**: Actual git commands

---

## 🔐 Security Notes

✅ **Safe by default:**
- Flask server only listens on `127.0.0.1` (local only)
- Token auth uses temporary URL injection
- Input validation prevents path traversal
- Original remotes are restored after operations

⚠️ **Never share token values:**
- Use environment variables: `export GITHUB_TOKEN=...`
- Don't commit tokens to git
- Use `.gitignore` for token files

---

## 📝 Example: Full Git Workflow

```
Copilot: "Clone my repo, check the status, create a feature branch, and tell me what changed"

Sequence:
1. git_clone {repo_url, dest}
2. git_status {repo_path}
3. git_checkout {repo_path, target: "feature/foo", create: true}
4. git_log {repo_path, n: 5}
```

---

**Happy coding! 🚀**
