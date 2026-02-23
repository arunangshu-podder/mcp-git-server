# mcp-git-server

Minimal MCP-style HTTP server to run common Git operations.

Features:
- Configure the `git` executable path via env or config file
- Exposes HTTP JSON endpoints for common git operations: clone, status, log, branch, fetch, pull, push
- Uses a whitelist to avoid arbitrary unsafe git commands

Quick start

1. Create a virtualenv and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. (Optional) Configure git path via env:

```bash
export GIT_PATH=/usr/bin/git
```

3. Run the server:

```bash
python run_server.py --host 0.0.0.0 --port 5000
```

4. Example: check repo status

```bash
curl -X POST http://localhost:5000/api/status -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo"}'
```

See the endpoint descriptions in `mcp_git_server/server.py`.

API Usage
---------

Below are common HTTP examples to call the MCP Git server endpoints.

- Status (human-readable, default):

```bash
curl -X POST http://localhost:8000/api/status \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo"}'
```

- Status (machine/porcelain):

```bash
curl -X POST http://localhost:8000/api/status \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo","human":false}'
```

- Clone (creates a new folder under `dest` if `dest` exists):

```bash
curl -X POST http://localhost:8000/api/clone \
  -H 'Content-Type: application/json' \
  -d '{"repo_url":"https://dev.azure.com/org/project/_git/repo","dest":"/path/to/parent"}'
```

If using token auth, set `ADO_PAT` or `GITHUB_TOKEN` in the environment before starting the server.

- Fetch a specific branch (with optional token-auth via `repo_url`):

```bash
export ADO_PAT=your_pat_here
curl -X POST http://localhost:8000/api/fetch \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo","remote":"origin","branch":"feature/foo","repo_url":"https://dev.azure.com/org/project/_git/repo"}'
```

- Pull / Push (use `repo_url` for token auth if needed):

```bash
curl -X POST http://localhost:8000/api/pull \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo","repo_url":"https://dev.azure.com/org/project/_git/repo"}'
```

- Checkout (switch branch); create new branch with `create=true`:

```bash
# checkout existing
curl -X POST http://localhost:8000/api/checkout \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo","target":"main"}'

# create and checkout
curl -X POST http://localhost:8000/api/checkout \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo","target":"new-branch","create":true}'
```

- Add files to index (`git add .` or `git add <file>`):

```bash
# add all
curl -X POST http://localhost:8000/api/add \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo"}'

# add single file
curl -X POST http://localhost:8000/api/add \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo","paths":"relative/path/file.txt"}'

# add multiple files
curl -X POST http://localhost:8000/api/add \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"/path/to/repo","paths":["file1.txt","dir/file2.java"]}'
```

Notes
-----
- Prefer setting tokens via environment variables (e.g., `export ADO_PAT=...`) rather than committing them to `config.yml`.
- The server will return JSON with `returncode`, `stdout`, `stderr`, and an optional `message` for many endpoints.
- See `mcp_git_server/server.py` for full endpoint behavior and `mcp_git_server/git_runner.py` for how git commands are executed.
