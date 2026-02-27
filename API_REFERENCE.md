# MCP Git Server - Complete API Reference

Comprehensive documentation for all 21 git operations available via MCP tools and HTTP endpoints.

---

## Table of Contents

1. [MCP Tools (for Copilot)](#mcp-tools-for-copilot)
2. [HTTP API Endpoints (for direct access)](#http-api-endpoints)
3. [Common Parameters](#common-parameters)
4. [Response Format](#response-format)
5. [Error Handling](#error-handling)

---

## MCP Tools (for Copilot)

These tools are available when using the MCP server with VS Code Copilot. Copilot automatically translates natural language requests into these tool calls.

### 1. `git_clone`
Clone a git repository.

**Parameters:**
- `repo_url` (string, **required**): Repository URL (https://github.com/user/repo.git)
- `dest` (string, optional): Destination path (defaults to current directory)
- `extra_args` (array of strings, optional): Additional git clone arguments (e.g., `["--depth", "1"]`)

**Example (natural language):**
```
"Clone https://github.com/torvalds/linux.git to ~/projects"
```

**Tool call:**
```json
{
  "name": "git_clone",
  "arguments": {
    "repo_url": "https://github.com/torvalds/linux.git",
    "dest": "~/projects"
  }
}
```

---

### 2. `git_status`
Get the status of a repository.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `human` (boolean, optional): Human-readable output (default: `true`)

**Example (natural language):**
```
"What's the status of my project at ~/my-repo?"
```

**Tool call:**
```json
{
  "name": "git_status",
  "arguments": {
    "repo_path": "~/my-repo",
    "human": true
  }
}
```

**Output formats:**
- `human: true` → Standard `git status` output with colors
- `human: false` → Porcelain format for parsing

---

### 3. `git_pull`
Pull changes from remote repository.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `remote` (string, optional): Remote name (default: `"origin"`)
- `branch` (string, optional): Branch name (default: `"main"`)
- `rebase` (boolean, optional): Use `--rebase` flag (default: `false`)
- `repo_url` (string, optional): Repository URL for token authentication

**Example (natural language):**
```
"Pull the latest changes from origin main with rebase"
```

**Tool call:**
```json
{
  "name": "git_pull",
  "arguments": {
    "repo_path": "~/my-repo",
    "remote": "origin",
    "branch": "main",
    "rebase": true
  }
}
```

**Note:** Token authentication is automatic if `GITHUB_TOKEN` or `ADO_PAT` is configured in environment.

---

### 4. `git_push`
Push changes to remote repository.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `remote` (string, optional): Remote name (default: `"origin"`)
- `branch` (string, optional): Branch name (default: current branch)
- `repo_url` (string, optional): Repository URL for token authentication

**Example (natural language):**
```
"Push my changes to origin main"
```

**Tool call:**
```json
{
  "name": "git_push",
  "arguments": {
    "repo_path": "~/my-repo",
    "remote": "origin",
    "branch": "main"
  }
}
```

---

### 5. `git_commit`
Commit staged changes with a message.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `message` (string, **required**): Commit message

**Example (natural language):**
```
"Commit the changes with message 'feat: add login feature'"
```

**Tool call:**
```json
{
  "name": "git_commit",
  "arguments": {
    "repo_path": "~/my-repo",
    "message": "feat: add login feature"
  }
}
```

---

### 6. `git_add`
Add files to the staging area.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `paths` (string or array of strings, optional): Files/directories to add (default: `"."` for all)

**Example (natural language):**
```
"Stage all changes in my repo"
"Add src/main.py and README.md to staging"
```

**Tool calls:**
```json
// Add all files
{
  "name": "git_add",
  "arguments": {
    "repo_path": "~/my-repo"
  }
}

// Add specific files
{
  "name": "git_add",
  "arguments": {
    "repo_path": "~/my-repo",
    "paths": ["src/main.py", "README.md"]
  }
}
```

---

### 7. `git_checkout`
Switch to a different branch or create a new branch.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `target` (string, **required**): Branch name or commit hash to checkout
- `create` (boolean, optional): Create new branch if it doesn't exist (default: `false`)

**Example (natural language):**
```
"Switch to feature-branch"
"Create and checkout a new branch called test-feature"
```

**Tool calls:**
```json
// Checkout existing branch
{
  "name": "git_checkout",
  "arguments": {
    "repo_path": "~/my-repo",
    "target": "feature-branch"
  }
}

// Create and checkout new branch
{
  "name": "git_checkout",
  "arguments": {
    "repo_path": "~/my-repo",
    "target": "test-feature",
    "create": true
  }
}
```

---

### 8. `git_branch`
Get the current branch name.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository

**Example (natural language):**
```
"What branch am I on?"
```

**Tool call:**
```json
{
  "name": "git_branch",
  "arguments": {
    "repo_path": "~/my-repo"
  }
}
```

**Returns:** Current branch name (e.g., `"main"`, `"feature/login"`)

---

### 9. `git_log`
Show recent commit history.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `n` (integer, optional): Number of commits to show (default: `20`)

**Example (natural language):**
```
"Show me the last 10 commits"
```

**Tool call:**
```json
{
  "name": "git_log",
  "arguments": {
    "repo_path": "~/my-repo",
    "n": 10
  }
}
```

**Output format:** One-line format with hash, author, date, and message

---

### 10. `git_fetch`
Fetch changes from remote without merging.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `remote` (string, optional): Remote name (default: `"origin"`)
- `branch` (string, optional): Specific branch to fetch (default: all branches)
- `repo_url` (string, optional): Repository URL for token authentication

**Example (natural language):**
```
"Fetch the latest changes from origin"
```

**Tool call:**
```json
{
  "name": "git_fetch",
  "arguments": {
    "repo_path": "~/my-repo",
    "remote": "origin"
  }
}
```

---

### 11. `git_merge`
Merge a branch into the current branch.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `branch` (string, **required**): Branch name to merge
- `no_ff` (boolean, optional): Use `--no-ff` flag to create a merge commit (default: `false`)
- `extra_args` (array of strings, optional): Additional git merge arguments

**Example (natural language):**
```
"Merge feature-branch into current branch"
"Merge develop with --no-ff"
```

**Tool calls:**
```json
// Simple merge
{
  "name": "git_merge",
  "arguments": {
    "repo_path": "~/my-repo",
    "branch": "feature-branch"
  }
}

// Merge with no-fast-forward
{
  "name": "git_merge",
  "arguments": {
    "repo_path": "~/my-repo",
    "branch": "develop",
    "no_ff": true
  }
}
```

**Note:** Merge conflicts must be resolved manually. If conflicts occur, the operation will return an error with conflict details.

---

### 12. `git_stash`
Manage git stashes (save, list, apply, pop, drop, clear, show).

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `action` (string, optional): Stash action - one of: `list`, `save`, `pop`, `apply`, `drop`, `clear`, `show` (default: `"list"`)
- `message` (string, optional): Stash message (for `save` action)
- `stash_index` (string, optional): Stash identifier like `stash@{0}` (for `pop`, `apply`, `drop`, `show` actions)
- `patch` (boolean, optional): Show as patch for `show` action (default: `false`)

**Example (natural language):**
```
"Stash my current changes"
"List all stashes"
"Apply stash@{0}"
"Pop the latest stash"
"Show stash@{1} as a patch"
```

**Tool calls:**
```json
// Save current changes
{
  "name": "git_stash",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "save",
    "message": "WIP: feature in progress"
  }
}

// List all stashes
{
  "name": "git_stash",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "list"
  }
}

// Apply specific stash
{
  "name": "git_stash",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "apply",
    "stash_index": "stash@{0}"
  }
}

// Pop latest stash
{
  "name": "git_stash",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "pop"
  }
}

// Show stash as patch
{
  "name": "git_stash",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "show",
    "stash_index": "stash@{1}",
    "patch": true
  }
}
```

**Stash Actions:**
- `list` - List all stashes
- `save` - Save current changes to stash
- `pop` - Apply and remove latest (or specified) stash
- `apply` - Apply stash without removing it
- `drop` - Remove a stash
- `clear` - Remove all stashes
- `show` - Show stash contents (optionally as patch)

---

### 13. `git_reset`
Reset current HEAD to specified state or unstage files.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `mode` (string, optional): Reset mode - one of: `soft`, `mixed`, `hard`, `merge`, `keep` (default: `"mixed"`)
- `target` (string, optional): Commit hash, branch, or ref to reset to (e.g., `"HEAD~1"`, `"origin/main"`)
- `paths` (array of strings, optional): File paths to unstage (when provided, mode is ignored)

**Example (natural language):**
```
"Reset to the previous commit"
"Undo the last commit but keep changes"
"Unstage all files"
"Hard reset to origin/main"
```

**Tool calls:**
```json
// Soft reset (undo commit, keep changes staged)
{
  "name": "git_reset",
  "arguments": {
    "repo_path": "~/my-repo",
    "mode": "soft",
    "target": "HEAD~1"
  }
}

// Mixed reset (undo commit and unstage, keep changes in working dir)
{
  "name": "git_reset",
  "arguments": {
    "repo_path": "~/my-repo",
    "mode": "mixed",
    "target": "HEAD~1"
  }
}

// Hard reset (discard all changes)
{
  "name": "git_reset",
  "arguments": {
    "repo_path": "~/my-repo",
    "mode": "hard",
    "target": "origin/main"
  }
}

// Unstage specific files
{
  "name": "git_reset",
  "arguments": {
    "repo_path": "~/my-repo",
    "paths": ["src/main.py", "README.md"]
  }
}
```

**Reset Modes:**
- `soft` - Move HEAD only, keep index and working directory unchanged
- `mixed` - Move HEAD and reset index, keep working directory (default)
- `hard` - Move HEAD, reset index and working directory (**DESTRUCTIVE**)
- `merge` - Reset but keep changes not in conflict with target
- `keep` - Reset but keep local changes

---

### 14. `git_config`
Get, set, unset, or list git configuration values.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `action` (string, optional): Configuration action - one of: `get`, `set`, `unset`, `list` (default: `"get"`)
- `key` (string, optional): Configuration key (e.g., `"user.name"`, `"user.email"`)
- `value` (string, optional): Value to set (required for `set` action)
- `global_scope` (boolean, optional): If true, operates on global config (default: `false`)

**Example (natural language):**
```
"Get the user name configuration"
"Set user email to john@example.com"
"List all configuration"
"Set the default editor to vim globally"
```

**Tool calls:**
```json
// Get configuration value
{
  "name": "git_config",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "get",
    "key": "user.name"
  }
}

// Set configuration value
{
  "name": "git_config",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "set",
    "key": "user.email",
    "value": "john@example.com"
  }
}

// Set global configuration
{
  "name": "git_config",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "set",
    "key": "core.editor",
    "value": "vim",
    "global_scope": true
  }
}

// List all configuration
{
  "name": "git_config",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "list"
  }
}

// Unset configuration value
{
  "name": "git_config",
  "arguments": {
    "repo_path": "~/my-repo",
    "action": "unset",
    "key": "user.signingkey"
  }
}
```

**Common Configuration Keys:**
- `user.name` - Your name for commits
- `user.email` - Your email for commits
- `core.editor` - Default text editor
- `core.autocrlf` - Line ending handling (true/false/input)
- `remote.origin.url` - Remote repository URL

---

### 15. `git_restore`
Restore working tree files or unstage changes (modern alternative to checkout for files).

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `paths` (array of strings, **required**): File paths to restore
- `source` (string, optional): Source to restore from (e.g., `"HEAD"`, `"HEAD~1"`, branch name)
- `staged` (boolean, optional): Restore staging area / unstage files (default: `false`)
- `worktree` (boolean, optional): Restore working tree (default: `false`)

**Example (natural language):**
```
"Restore main.py from HEAD"
"Unstage README.md"
"Discard all changes in src/utils/*"
"Restore index.html from the previous commit"
```

**Tool calls:**
```json
// Restore file from index (discard working directory changes)
{
  "name": "git_restore",
  "arguments": {
    "repo_path": "~/my-repo",
    "paths": ["src/main.py"]
  }
}

// Unstage file (restore index from HEAD)
{
  "name": "git_restore",
  "arguments": {
    "repo_path": "~/my-repo",
    "paths": ["README.md"],
    "staged": true
  }
}

// Restore file from specific commit
{
  "name": "git_restore",
  "arguments": {
    "repo_path": "~/my-repo",
    "paths": ["index.html"],
    "source": "HEAD~1"
  }
}

// Discard all changes (staged and working)
{
  "name": "git_restore",
  "arguments": {
    "repo_path": "~/my-repo",
    "paths": ["."],
    "staged": true,
    "worktree": true
  }
}
```

**Restore Modes:**
- Default (no flags): Restore working tree from index
- `staged: true` - Restore index from HEAD (unstage files)
- `worktree: true` - Explicitly restore working tree
- Both flags: Discard all changes (staged and unstaged)

---

## Merge Conflict Resolution Tools

### 16. `git_conflict_status`
Check if repository is in merge/rebase state and list all conflicted files.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository

**Returns:**
```json
{
  "in_merge": boolean,
  "in_rebase": boolean,
  "in_cherrypick": boolean,
  "conflicted_files": ["file1.js", "file2.py"],
  "conflict_count": integer
}
```

**Example (natural language):**
```
"Check for merge conflicts in my repo"
"What conflicts do I have?"
"Show conflicted files"
```

**Tool call:**
```json
{
  "name": "git_conflict_status",
  "arguments": {
    "repo_path": "~/my-repo"
  }
}
```

---

### 17. `git_show_conflicts`
Show a conflicted file with conflict markers so you can see both versions.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `file_path` (string, **required**): Relative path to conflicted file (e.g., `src/main.js`)

**Returns:**
- File content with conflict markers intact:
  ```
  <<<<<<< HEAD
  your code
  =======
  their code
  >>>>>>> branch-name
  ```

**Example (natural language):**
```
"Show me the conflicts in src/main.js"
"What's the merge conflict in README.md?"
```

**Tool call:**
```json
{
  "name": "git_show_conflicts",
  "arguments": {
    "repo_path": "~/my-repo",
    "file_path": "src/main.js"
  }
}
```

**Note:** User should manually edit this file in VS Code to choose which code to keep, then mark it as resolved with `git_add`.

---

### 18. `git_diff_conflict`
Show diffs for conflicted files to understand what each side changed.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `file_path` (string, optional): Specific file to show, or all conflicts if omitted

**Returns:**
- Unified diff showing changes from both sides

**Example (natural language):**
```
"Show me what's different in the conflicted files"
"Diff of the merge conflict in config.yaml"
```

**Tool call:**
```json
{
  "name": "git_diff_conflict",
  "arguments": {
    "repo_path": "~/my-repo",
    "file_path": "config.yaml"
  }
}
```

---

### 19. `git_abort_merge`
Abort an ongoing merge, rebase, or cherry-pick operation.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository

**Example (natural language):**
```
"Cancel this merge"
"Abort the merge"
"Stop the rebase"
```

**Tool call:**
```json
{
  "name": "git_abort_merge",
  "arguments": {
    "repo_path": "~/my-repo"
  }
}
```

---

### 20. `git_merge_continue`
Complete a merge after manually resolving all conflicts.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository
- `message` (string, optional): Custom merge commit message

**Example (natural language):**
```
"Complete the merge"
"Finish merging with message 'Merge feature-branch'"
```

**Tool calls:**
```json
// Complete merge with default message
{
  "name": "git_merge_continue",
  "arguments": {
    "repo_path": "~/my-repo"
  }
}

// Complete merge with custom message
{
  "name": "git_merge_continue",
  "arguments": {
    "repo_path": "~/my-repo",
    "message": "Merge feature: add login"
  }
}
```

**Requirements:**
- All conflicted files must be resolved and staged with `git_add`
- Must be in a merge state (initiated by `git_merge`)

---

### 21. `git_rebase_continue`
Continue rebasing after manually resolving conflicts in current commit.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository

**Example (natural language):**
```
"Continue the rebase"
"Move to next conflict"
```

**Tool call:**
```json
{
  "name": "git_rebase_continue",
  "arguments": {
    "repo_path": "~/my-repo"
  }
}
```

**Note:** May return conflicts for next commit or complete if all resolved. User must stage changes before calling this.

---

### 22. `git_rebase_abort`
Abort an ongoing rebase operation and return to previous state.

**Parameters:**
- `repo_path` (string, **required**): Path to the git repository

**Example (natural language):**
```
"Cancel this rebase"
"Abort the rebase"
```

**Tool call:**
```json
{
  "name": "git_rebase_abort",
  "arguments": {
    "repo_path": "~/my-repo"
  }
}
```

---

## HTTP API Endpoints

If you're accessing the Flask server directly (not via MCP), use these HTTP endpoints.

**Base URL:** `http://127.0.0.1:5000/api`

### General Format

**Request:**
```http
POST /api/{endpoint}
Content-Type: application/json

{
  "param1": "value1",
  "param2": "value2"
}
```

**Response:**
```json
{
  "returncode": 0,
  "stdout": "command output",
  "stderr": "",
  "message": "Operation completed successfully"
}
```

---

### Endpoint Details

#### `POST /api/clone`
Clone a repository.

**Request body:**
```json
{
  "repo_url": "https://github.com/user/repo.git",
  "dest": "/path/to/destination",
  "extra_args": ["--depth", "1"]
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/clone \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/torvalds/linux.git","dest":"/tmp/linux"}'
```

---

#### `POST /api/status`
Get repository status.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "human": true
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/status \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","human":true}'
```

---

#### `POST /api/pull`
Pull from remote.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "remote": "origin",
  "branch": "main",
  "rebase": true
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/pull \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","rebase":true}'
```

---

#### `POST /api/push`
Push to remote.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "remote": "origin",
  "branch": "main"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/push \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","branch":"feature-branch"}'
```

---

#### `POST /api/commit`
Commit staged changes.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "message": "feat: add new feature"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/commit \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","message":"Fix bug in login"}'
```

---

#### `POST /api/add`
Add files to staging area.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "paths": ["src/main.py", "README.md"]
}
```

**curl example:**
```bash
# Add all files
curl -X POST http://127.0.0.1:5000/api/add \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo"}'

# Add specific files
curl -X POST http://127.0.0.1:5000/api/add \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","paths":["src/app.py"]}'
```

---

#### `POST /api/checkout`
Checkout a branch.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "target": "feature-branch",
  "create": false
}
```

**curl example:**
```bash
# Checkout existing branch
curl -X POST http://127.0.0.1:5000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","target":"main"}'

# Create new branch
curl -X POST http://127.0.0.1:5000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","target":"new-feature","create":true}'
```

---

#### `POST /api/branch`
Get current branch name.

**Request body:**
```json
{
  "repo_path": "/path/to/repo"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/branch \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo"}'
```

---

#### `POST /api/log`
Show commit history.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "n": 20
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/log \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","n":10}'
```

---

#### `POST /api/fetch`
Fetch from remote.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "remote": "origin",
  "branch": "main"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","remote":"origin"}'
```

---

#### `POST /api/merge`
Merge a branch into current branch.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "branch": "feature-branch",
  "no_ff": true,
  "extra_args": ["--squash"]
}
```

**curl examples:**
```bash
# Simple merge
curl -X POST http://127.0.0.1:5000/api/merge \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","branch":"feature-branch"}'

# Merge with no-fast-forward
curl -X POST http://127.0.0.1:5000/api/merge \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","branch":"develop","no_ff":true}'
```

**Note:** If merge conflicts occur, the operation will fail and return conflict details in stderr. Conflicts must be resolved manually.

---

#### `POST /api/stash`
Manage git stashes.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "action": "save",
  "message": "WIP: feature in progress",
  "stash_index": "stash@{0}",
  "patch": false
}
```

**curl examples:**
```bash
# Save/stash changes
curl -X POST http://127.0.0.1:5000/api/stash \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"save","message":"WIP: testing"}'

# List all stashes
curl -X POST http://127.0.0.1:5000/api/stash \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"list"}'

# Apply stash
curl -X POST http://127.0.0.1:5000/api/stash \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"apply","stash_index":"stash@{0}"}'

# Pop latest stash
curl -X POST http://127.0.0.1:5000/api/stash \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"pop"}'

# Drop specific stash
curl -X POST http://127.0.0.1:5000/api/stash \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"drop","stash_index":"stash@{1}"}'

# Clear all stashes
curl -X POST http://127.0.0.1:5000/api/stash \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"clear"}'

# Show stash as patch
curl -X POST http://127.0.0.1:5000/api/stash \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"show","stash_index":"stash@{0}","patch":true}'
```

**Available actions:**
- `list` - List all stashes (default)
- `save` - Save current changes to stash
- `pop` - Apply and remove latest (or specified) stash
- `apply` - Apply stash without removing it
- `drop` - Remove a specific stash
- `clear` - Remove all stashes
- `show` - Show stash contents (optionally as patch)

---

#### `POST /api/reset`
Reset current HEAD to specified state or unstage files.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "mode": "mixed",
  "target": "HEAD~1",
  "paths": ["file1.txt", "file2.txt"]
}
```

**curl examples:**
```bash
# Soft reset (undo commit, keep changes staged)
curl -X POST http://127.0.0.1:5000/api/reset \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","mode":"soft","target":"HEAD~1"}'

# Mixed reset (undo commit and unstage)
curl -X POST http://127.0.0.1:5000/api/reset \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","mode":"mixed","target":"HEAD~1"}'

# Hard reset (discard all changes - DESTRUCTIVE)
curl -X POST http://127.0.0.1:5000/api/reset \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","mode":"hard","target":"origin/main"}'

# Unstage specific files
curl -X POST http://127.0.0.1:5000/api/reset \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","paths":["src/main.py","README.md"]}'
```

**Reset modes:**
- `soft` - Move HEAD only, keep index and working directory
- `mixed` - Move HEAD and reset index (default)
- `hard` - Move HEAD, reset index and working directory (**DESTRUCTIVE**)
- `merge` - Reset but keep changes not in conflict
- `keep` - Reset but keep local changes

**Note:** When `paths` is provided, only those files are unstaged (mode is ignored).

---

#### `POST /api/config`
Get, set, unset, or list git configuration values.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "action": "set",
  "key": "user.email",
  "value": "john@example.com",
  "global_scope": false
}
```

**curl examples:**
```bash
# Get configuration value
curl -X POST http://127.0.0.1:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"get","key":"user.name"}'

# Set configuration value
curl -X POST http://127.0.0.1:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"set","key":"user.email","value":"john@example.com"}'

# Set global configuration
curl -X POST http://127.0.0.1:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"set","key":"core.editor","value":"vim","global_scope":true}'

# List all configuration
curl -X POST http://127.0.0.1:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"list"}'

# Unset configuration value
curl -X POST http://127.0.0.1:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","action":"unset","key":"user.signingkey"}'
```

**Configuration actions:**
- `get` - Get a configuration value (default)
- `set` - Set a configuration value
- `unset` - Remove a configuration value
- `list` - List all configuration

**Common config keys:** `user.name`, `user.email`, `core.editor`, `core.autocrlf`, `remote.origin.url`

---

#### `POST /api/restore`
Restore working tree files or unstage changes.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "paths": ["src/main.py", "README.md"],
  "source": "HEAD",
  "staged": false,
  "worktree": false
}
```

**curl examples:**
```bash
# Restore file from index (discard working directory changes)
curl -X POST http://127.0.0.1:5000/api/restore \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","paths":["src/main.py"]}'

# Unstage file (restore index from HEAD)
curl -X POST http://127.0.0.1:5000/api/restore \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","paths":["README.md"],"staged":true}'

# Restore file from specific commit
curl -X POST http://127.0.0.1:5000/api/restore \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","paths":["index.html"],"source":"HEAD~1"}'

# Discard all changes (staged and working)
curl -X POST http://127.0.0.1:5000/api/restore \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","paths":["."],"staged":true,"worktree":true}'
```

**Restore modes:**
- Default (no flags): Restore working tree from index
- `"staged": true` - Restore index from HEAD (unstage files)
- `"worktree": true` - Explicitly restore working tree
- Both flags: Discard all changes

**Note:** `git restore` is the modern alternative to `git checkout` for restoring files (Git 2.23+).

---

#### `POST /api/conflict_status`
Get merge conflict status: current merge state, conflicted files, and resolved files.

**Request body:**
```json
{
  "repo_path": "/path/to/repo"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/conflict_status \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo"}'
```

**Response example:**
```json
{
  "merging": true,
  "rebasing": false,
  "conflicted_files": ["src/app.py", "config.json"],
  "resolved_files": ["README.md"],
  "merge_head": "abc123def456"
}
```

**Use cases:**
- Detect if merge/rebase is in progress
- List files with unresolved conflicts
- Check which files have been resolved

---

#### `POST /api/show_conflicts`
Display file content with Git conflict markers to identify conflicting sections.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "file_path": "src/app.py"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/show_conflicts \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","file_path":"src/app.py"}'
```

**Response example:**
```json
{
  "file_path": "src/app.py",
  "content": "def greet():\n<<<<<<< HEAD\n    return 'Hello'  # Current branch\n=======\n    return 'Hi'  # Incoming branch\n>>>>>>> feature-branch\n"
}
```

**Conflict markers:**
- `<<<<<<< HEAD` - Start of current branch changes
- `=======` - Separator between branches
- `>>>>>>> <branch>` - End of incoming branch changes

---

#### `POST /api/diff_conflict`
Show unified diff of conflicting changes to understand what each side changed.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "file_path": "src/app.py"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/diff_conflict \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","file_path":"src/app.py"}'
```

**Response example:**
```json
{
  "diff": "diff --git a/src/app.py b/src/app.py\nindex abc123..def456 100644\n--- a/src/app.py\n+++ b/src/app.py\n@@ -1,5 +1,5 @@\n def greet():\n-    return 'Hello'\n+    return 'Hi'\n"
}
```

**Use cases:**
- Understand what changed on each branch
- Decide which changes to keep
- See context around conflicts

---

#### `POST /api/abort_merge`
Cancel the current merge, rebase, or cherry-pick and return to the state before the operation started.

**Request body:**
```json
{
  "repo_path": "/path/to/repo"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/abort_merge \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo"}'
```

**Response example:**
```json
{
  "success": true,
  "message": "Merge aborted"
}
```

**Supported operations:**
- Aborts ongoing merge operations
- Aborts ongoing rebase operations
- Aborts ongoing cherry-pick operations

**Use cases:**
- Cancel merge if conflicts are too complex
- Abort rebase and start over with different strategy
- Give up on current merge attempt

---

#### `POST /api/merge_continue`
Complete the merge after all conflicts are manually resolved and staged.

**Request body:**
```json
{
  "repo_path": "/path/to/repo",
  "message": "Merge branch 'feature' into 'main'"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/merge_continue \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo","message":"Merge main into feature"}'
```

**Response example:**
```json
{
  "success": true,
  "message": "Merge completed successfully"
}
```

**Workflow:**
1. Show conflicts with `git_show_conflicts`
2. User edits files in VS Code to resolve conflicts
3. Stage resolved files with `git_add`
4. Call `git_merge_continue` to complete merge
5. Creates a merge commit with specified message

**Note:** All conflicts must be resolved and files staged before calling this endpoint.

---

#### `POST /api/rebase_continue`
Continue rebase after manually resolving conflicts for the current commit.

**Request body:**
```json
{
  "repo_path": "/path/to/repo"
}
```

**curl example:**
```bash
curl -X POST http://127.0.0.1:5000/api/rebase_continue \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"/Users/user/my-repo"}'
```

**Response example:**
```json
{
  "success": true,
  "message": "Rebase continued, processing next commit"
}
```

**Workflow for rebasing:**
1. Start rebase with `git_checkout` or pull with rebase option
2. When conflicts occur, `git_conflict_status` detects rebase state
3. Show conflicts with `git_show_conflicts`
4. User edits files in VS Code to resolve
5. Stage resolved files with `git_add`
6. Call `git_rebase_continue` to proceed to next commit
7. Repeat until rebase completes or another conflict occurs

**Note:** Use `git_abort_merge` to cancel rebase if needed (`git rebase --abort`).

---

#### `GET /api/health`
Health check endpoint.

**curl example:**
```bash
curl http://127.0.0.1:5000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-25T10:30:00Z"
}
```

---

## Common Parameters

### `repo_path`
- **Type:** string
- **Description:** Absolute or relative path to a git repository
- **Example:** `/Users/user/my-project` or `~/Documents/code/myapp`

### `repo_url`
- **Type:** string
- **Description:** Git repository URL (https:// or git://)
- **Example:** `https://github.com/user/repo.git`
- **Note:** For private repos, ensure `GITHUB_TOKEN` or `ADO_PAT` is configured

### `remote`
- **Type:** string
- **Default:** `"origin"`
- **Description:** Name of the git remote

### `branch`
- **Type:** string
- **Description:** Branch name
- **Example:** `main`, `develop`, `feature/login`

---

## Response Format

All HTTP endpoints return JSON with this structure:

```json
{
  "returncode": 0,
  "stdout": "command output here",
  "stderr": "error output (if any)",
  "message": "Human-readable message (optional)"
}
```

### Return Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Generic git error |
| `124` | Timeout (operation exceeded configured timeout) |
| `127` | Git executable not found |
| `128+` | Git-specific errors (see git documentation) |

---

## Error Handling

### Common Errors

#### 1. Repository Not Found
```json
{
  "returncode": 128,
  "stdout": "",
  "stderr": "fatal: not a git repository",
  "message": "The specified path is not a git repository"
}
```

**Solution:** Verify `repo_path` points to a valid git repository.

---

#### 2. Authentication Failed
```json
{
  "returncode": 128,
  "stdout": "",
  "stderr": "fatal: Authentication failed",
  "message": "Invalid or missing credentials"
}
```

**Solution:** 
- Set `GITHUB_TOKEN` or `ADO_PAT` in environment
- Verify token has correct permissions
- Check token hasn't expired

---

#### 3. Timeout
```json
{
  "returncode": 124,
  "stdout": "",
  "stderr": "Timeout after 30s",
  "message": "Operation timed out"
}
```

**Solution:** 
- Increase `GIT_TIMEOUT` environment variable
- Check network connectivity
- Try with smaller repository or shallow clone

---

#### 4. Git Not Found
```json
{
  "returncode": 127,
  "stdout": "",
  "stderr": "git executable not found: /usr/bin/git",
  "message": "Git is not installed or not in PATH"
}
```

**Solution:**
- Install git: https://git-scm.com/downloads
- Ensure git is in PATH
- Set `GIT_PATH` environment variable

---

## Environment Variables

Configure these in your `mcp.json` or shell environment:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | No | - | GitHub Personal Access Token |
| `ADO_PAT` | No | - | Azure DevOps Personal Access Token |
| `GIT_TIMEOUT` | No | `30` | Operation timeout in seconds |
| `GIT_PATH` | No | Auto-detected | Path to git executable |
| `MCP_GIT_SERVER_URL` | No | `http://127.0.0.1:5000` | Flask server URL |
| `MCP_DEBUG` | No | `0` | Enable debug logging (`1` to enable) |
| `GIT_TOOLS_DEBUG` | No | `0` | Enable git tools debug (`1` to enable) |

---

## Complete Usage Example

### Workflow: Clone, Modify, Commit, Push

**Using Copilot (natural language):**
```
1. "Clone https://github.com/myorg/myrepo.git to ~/projects"
2. "What's the status of ~/projects/myrepo?"
3. "Stage all changes in ~/projects/myrepo"
4. "Commit with message 'Update documentation'"
5. "Push to origin main"
```

**Using HTTP API (curl):**
```bash
# 1. Clone
curl -X POST http://127.0.0.1:5000/api/clone \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/myorg/myrepo.git","dest":"~/projects"}'

# 2. Check status
curl -X POST http://127.0.0.1:5000/api/status \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"~/projects/myrepo"}'

# 3. Stage changes
curl -X POST http://127.0.0.1:5000/api/add \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"~/projects/myrepo"}'

# 4. Commit
curl -X POST http://127.0.0.1:5000/api/commit \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"~/projects/myrepo","message":"Update documentation"}'

# 5. Push
curl -X POST http://127.0.0.1:5000/api/push \
  -H "Content-Type: application/json" \
  -d '{"repo_path":"~/projects/myrepo","remote":"origin","branch":"main"}'
```

---

## See Also

- [MCP_SETUP.md](MCP_SETUP.md) - VS Code Copilot integration guide
- [TOKEN_AUTH_GUIDE.md](TOKEN_AUTH_GUIDE.md) - Token authentication setup
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [README.md](README.md) - Project overview

---

## Support

For issues or questions:
1. Check the error response for specific error messages
2. Enable debug mode: `export MCP_DEBUG=1` or `export GIT_TOOLS_DEBUG=1`
3. Review logs in VS Code Output panel (for MCP) or terminal (for HTTP)
4. Verify git is installed: `git --version`
5. Test tokens: See [TOKEN_AUTH_GUIDE.md](TOKEN_AUTH_GUIDE.md)
