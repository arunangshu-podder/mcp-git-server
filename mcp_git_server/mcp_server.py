"""
MCP Server for Git operations.

This module exposes git operations as MCP tools for VS Code Copilot.
It communicates with the Flask HTTP server running locally and speaks
MCP JSON-RPC 2.0 over stdio (Content-Length framing).
"""

import json
import os
import sys
from typing import Any, Optional

# MCP Tool Definitions
TOOLS = [
    {
        "name": "git_clone",
        "description": "Clone a git repository",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_url": {
                    "type": "string",
                    "description": "Repository URL (https://...)"
                },
                "dest": {
                    "type": "string",
                    "description": "Destination path (optional)"
                },
                "extra_args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Extra git clone arguments (optional)"
                }
            },
            "required": ["repo_url"]
        }
    },
    {
        "name": "git_status",
        "description": "Get repository status",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "human": {
                    "type": "boolean",
                    "description": "Human-readable output (default: true)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_pull",
        "description": "Pull from remote (git pull [remote] [branch] [--rebase])",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "remote": {
                    "type": "string",
                    "description": "Remote name (default: origin)"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (default: main)"
                },
                "rebase": {
                    "type": "boolean",
                    "description": "Use --rebase (default: false)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_push",
        "description": "Push to remote (git push [remote] [branch])",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "remote": {
                    "type": "string",
                    "description": "Remote name (default: origin)"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (default: main)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_commit",
        "description": "Commit staged changes (git commit -m '<message>')",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "message": {
                    "type": "string",
                    "description": "Commit message"
                }
            },
            "required": ["repo_path", "message"]
        }
    },
    {
        "name": "git_add",
        "description": "Add files to index (git add)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "paths": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}}
                    ],
                    "description": "Paths to add (default: . for all files)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_checkout",
        "description": "Checkout a branch (git checkout <branch>)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "target": {
                    "type": "string",
                    "description": "Branch or commit to checkout"
                },
                "create": {
                    "type": "boolean",
                    "description": "Create new branch if it doesn't exist (default: false)"
                }
            },
            "required": ["repo_path", "target"]
        }
    },
    {
        "name": "git_branch",
        "description": "Get current branch name",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_log",
        "description": "Show recent commits (git log)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "n": {
                    "type": "integer",
                    "description": "Number of commits to show (default: 20)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_fetch",
        "description": "Fetch from remote (git fetch)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "remote": {
                    "type": "string",
                    "description": "Remote name (optional)"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (optional)"
                },
                "repo_url": {
                    "type": "string",
                    "description": "Repository URL for token auth (optional)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_merge",
        "description": "Merge a branch into current branch (git merge <branch>)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name to merge (required)"
                },
                "no_ff": {
                    "type": "boolean",
                    "description": "Use --no-ff flag to create a merge commit (default: false)"
                },
                "extra_args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional git merge arguments (optional)"
                }
            },
            "required": ["repo_path", "branch"]
        }
    },
    {
        "name": "git_stash",
        "description": "Git stash operations (list, save, pop, apply, drop, clear, show)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "action": {
                    "type": "string",
                    "enum": ["list", "save", "pop", "apply", "drop", "clear", "show"],
                    "description": "Stash action to perform (default: list)"
                },
                "message": {
                    "type": "string",
                    "description": "Stash message (for 'save' action)"
                },
                "stash_index": {
                    "type": "string",
                    "description": "Stash identifier (e.g., 'stash@{0}') for pop, apply, drop, or show actions"
                },
                "patch": {
                    "type": "boolean",
                    "description": "Show as patch for 'show' action (default: false)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_reset",
        "description": "Reset current HEAD to specified state (soft, mixed, hard) or unstage files",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "mode": {
                    "type": "string",
                    "enum": ["soft", "mixed", "hard", "merge", "keep"],
                    "description": "Reset mode (default: mixed)"
                },
                "target": {
                    "type": "string",
                    "description": "Commit hash, branch, or ref to reset to (e.g., 'HEAD~1', 'origin/main')"
                },
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "File paths to unstage (when provided, mode is ignored)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_config",
        "description": "Get, set, unset, or list git configuration values",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "action": {
                    "type": "string",
                    "enum": ["get", "set", "unset", "list"],
                    "description": "Configuration action (default: get)"
                },
                "key": {
                    "type": "string",
                    "description": "Configuration key (e.g., 'user.name', 'user.email')"
                },
                "value": {
                    "type": "string",
                    "description": "Value to set (required for 'set' action)"
                },
                "global_scope": {
                    "type": "boolean",
                    "description": "If true, operates on global config (default: false)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_restore",
        "description": "Restore working tree files or unstage changes (modern alternative to checkout for files)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "File paths to restore (required)"
                },
                "source": {
                    "type": "string",
                    "description": "Source to restore from (e.g., 'HEAD', 'HEAD~1', branch name)"
                },
                "staged": {
                    "type": "boolean",
                    "description": "Restore staging area (unstage files, default: false)"
                },
                "worktree": {
                    "type": "boolean",
                    "description": "Restore working tree (default: false)"
                }
            },
            "required": ["repo_path", "paths"]
        }
    },
    {
        "name": "git_conflict_status",
        "description": "Check if in merge/rebase state and list conflicted files",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_show_conflicts",
        "description": "Show a conflicted file with conflict markers to view both versions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "file_path": {
                    "type": "string",
                    "description": "Relative path to conflicted file (e.g., 'src/main.py')"
                }
            },
            "required": ["repo_path", "file_path"]
        }
    },
    {
        "name": "git_diff_conflict",
        "description": "Show diffs for conflicted files to understand context",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "file_path": {
                    "type": "string",
                    "description": "Optional specific file (if None, shows all conflicts)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_abort_merge",
        "description": "Abort ongoing merge, rebase, or cherry-pick operation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_merge_continue",
        "description": "Complete a merge after manually resolving all conflicts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                },
                "message": {
                    "type": "string",
                    "description": "Custom merge commit message (optional)"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_rebase_continue",
        "description": "Continue rebase after manually resolving conflicts in current commit",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                }
            },
            "required": ["repo_path"]
        }
    },
    {
        "name": "git_rebase_abort",
        "description": "Abort an ongoing rebase operation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to repository"
                }
            },
            "required": ["repo_path"]
        }
    }
]


def call_git_endpoint(endpoint: str, data: dict, server_url: str = "http://127.0.0.1:5000") -> dict:
    """Call the Flask git server endpoint via HTTP."""
    import urllib.request
    import urllib.error
    
    debug = os.environ.get("MCP_DEBUG") == "1"
    
    # Allow override via environment variable
    server_url = os.environ.get("MCP_GIT_SERVER_URL", server_url)
    
    url = f"{server_url}/api/{endpoint}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode('utf-8')
    
    if debug:
        print(f"[MCP_DEBUG] calling {endpoint} on {server_url} with data: {str(data)[:200]}")
    
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if debug:
                print(f"[MCP_DEBUG] got response: {str(result)[:200]}")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        if debug:
            print(f"[MCP_DEBUG] HTTP {e.code}: {error_body[:200]}")
        return {
            "error": f"HTTP {e.code}",
            "details": error_body
        }
    except Exception as e:
        if debug:
            print(f"[MCP_DEBUG] exception: {str(e)}")
        return {"error": str(e)}


def process_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Process a tool call and return the result as a dict."""
    
    endpoint_map = {
        "git_clone": "clone",
        "git_status": "status",
        "git_pull": "pull",
        "git_push": "push",
        "git_commit": "commit",
        "git_add": "add",
        "git_checkout": "checkout",
        "git_branch": "branch",
        "git_log": "log",
        "git_fetch": "fetch",
        "git_merge": "merge",
        "git_stash": "stash",
        "git_reset": "reset",
        "git_config": "config",
        "git_restore": "restore",
        "git_conflict_status": "conflict_status",
        "git_show_conflicts": "show_conflicts",
        "git_diff_conflict": "diff_conflict",
        "git_abort_merge": "abort_merge",
        "git_merge_continue": "merge_continue",
        "git_rebase_continue": "rebase_continue",
        "git_rebase_abort": "rebase_abort"
    }
    
    if tool_name not in endpoint_map:
        return {"error": f"Unknown tool: {tool_name}"}
    
    endpoint = endpoint_map[tool_name]
    result = call_git_endpoint(endpoint, tool_input)
    
    return result


def _read_message() -> Optional[dict]:
    """Read one JSON-RPC message using line-delimited JSON format.
    
    VS Code Copilot sends line-delimited JSON (one message per line),
    NOT Content-Length framed messages.
    """
    debug = os.environ.get("MCP_DEBUG") == "1"
    
    try:
        raw_line = sys.stdin.buffer.readline()
        if not raw_line:
            if debug:
                print(f"[MCP_DEBUG] EOF on stdin")
            return None
        
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line:
            if debug:
                print(f"[MCP_DEBUG] empty line, skipping")
            return None
        
        if debug:
            print(f"[MCP_DEBUG] received line: {line[:100]}")
        
        msg = json.loads(line)
        if debug:
            print(f"[MCP_DEBUG] parsed: method={msg.get('method')}, id={msg.get('id')}")
        return msg
    except json.JSONDecodeError as e:
        if debug:
            print(f"[MCP_DEBUG] JSON decode error: {e}")
        return None
    except Exception as e:
        if debug:
            print(f"[MCP_DEBUG] error reading message: {e}")
        return None


def _write_message(payload: dict) -> None:
    """Write one JSON-RPC message using line-delimited JSON format.
    
    Sends one JSON object per line (newline-delimited JSON / NDJSON).
    """
    debug = os.environ.get("MCP_DEBUG") == "1"
    try:
        data = json.dumps(payload)
        sys.stdout.buffer.write((data + "\n").encode("utf-8"))
        sys.stdout.buffer.flush()
        if debug:
            print(f"[MCP_DEBUG] wrote: {data[:100]}")
    except Exception as e:
        if debug:
            print(f"[MCP_DEBUG] error writing message: {e}", file=sys.stderr)


def _make_error(code: int, message: str, request_id: Optional[Any]) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def _handle_request(request: dict) -> Optional[dict]:
    """Handle one JSON-RPC request."""
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"list": True, "call": True},
            },
            "serverInfo": {
                "name": "MCP Git Server",
                "version": "0.1.0",
            },
        }
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    if method == "tools/list":
        result = {"tools": TOOLS}
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        tool_result = process_tool_call(tool_name, tool_args)
        content = [{"type": "text", "text": json.dumps(tool_result)}]
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": content}}

    if method == "notifications/initialized":
        return None

    return _make_error(-32601, f"Method not found: {method}", request_id)


def main():
    """Main entry point for MCP server (JSON-RPC over stdio)."""
    print("MCP Git Server started", file=sys.stderr)
    print("Awaiting MCP JSON-RPC requests...", file=sys.stderr)

    try:
        while True:
            request = _read_message()
            if request is None:
                break
            try:
                if request.get("jsonrpc") != "2.0":
                    response = _make_error(-32600, "Invalid JSON-RPC version", request.get("id"))
                else:
                    response = _handle_request(request)
                if response is not None:
                    _write_message(response)
            except Exception as exc:
                response = _make_error(-32603, f"Internal error: {exc}", request.get("id"))
                _write_message(response)
    except KeyboardInterrupt:
        print("MCP Git Server stopped", file=sys.stderr)


if __name__ == "__main__":
    main()
