from flask import Flask, request, jsonify
from mcp_git_server.config import load_config
from mcp_git_server.git_tools import GitRunner
import os

app = Flask(__name__)
config = load_config()
runner = GitRunner(
    git_path=config.get("git_path"),
    github_token=config.get("github_token", ""),
    ado_pat=config.get("ado_pat", ""),
    timeout=config.get("timeout", 30),
)


def make_response(code, stdout, stderr):
    return jsonify({'returncode': code, 'stdout': stdout, 'stderr': stderr})


@app.route('/api/clone', methods=['POST'])
def clone():
    data = request.get_json() or {}
    repo = data.get('repo_url')
    dest = data.get('dest')
    if not repo:
        return jsonify({'error': 'repo_url required'}), 400
    rc, out, err = runner.clone(repo, dest, data.get('extra_args'))
    message = 'Clone successful' if rc == 0 else 'Clone failed'
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/status', methods=['POST'])
def status():
    data = request.get_json() or {}
    repo = data.get('repo_path')
    human = bool(data.get('human', True))
    if not repo or not os.path.exists(repo):
        return jsonify({'error': 'valid repo_path required'}), 400
    rc, out, err = runner.status(repo, human=human)
    return make_response(rc, out, err)


@app.route('/api/log', methods=['POST'])
def log():
    data = request.get_json() or {}
    repo = data.get('repo_path')
    n = int(data.get('n', 20))
    if not repo or not os.path.exists(repo):
        return jsonify({'error': 'valid repo_path required'}), 400
    rc, out, err = runner.log(repo, n=n)
    return make_response(rc, out, err)


@app.route('/api/branch', methods=['POST'])
def branch():
    data = request.get_json() or {}
    repo = data.get('repo_path')
    if not repo or not os.path.exists(repo):
        return jsonify({'error': 'valid repo_path required'}), 400
    rc, out, err = runner.branch(repo)
    return make_response(rc, out, err)


@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json() or {}
    repo = data.get('repo_path')
    target = data.get('target')
    create = bool(data.get('create', False))
    if not repo or not os.path.exists(repo):
        return jsonify({'error': 'valid repo_path required'}), 400
    if not target:
        return jsonify({'error': 'target (branch or commit) required'}), 400
    rc, out, err = runner.checkout(repo, target=target, create=create)
    message = 'Checkout successful' if rc == 0 else 'Checkout failed'
    # If checkout succeeded, git may write the success message to stderr.
    # Combine stderr into stdout for successful operations so clients receive
    # the message in `stdout`.
    if rc == 0 and err:
        out = (out or '') + err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/add', methods=['POST'])
def add():
    data = request.get_json() or {}
    repo = data.get('repo_path')
    paths = data.get('paths')
    if not repo or not os.path.exists(repo):
        return jsonify({'error': 'valid repo_path required'}), 400
    rc, out, err = runner.add(repo, paths)
    message = 'Add successful' if rc == 0 else 'Add failed'
    # Surface informational messages in stdout on success
    if rc == 0 and err:
        out = (out or '') + err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})
 


@app.route('/api/fetch', methods=['POST'])
def fetch():
    data = request.get_json() or {}
    repo = data.get('repo_path')
    remote = data.get('remote')
    branch = data.get('branch')
    repo_url = data.get('repo_url')
    if not repo or not os.path.exists(repo):
        return jsonify({'error': 'valid repo_path required'}), 400
    rc, out, err = runner.fetch(repo, remote=remote, branch=branch, repo_url=repo_url)
    # Git frequently writes informational messages (like fetch summaries) to stderr.
    # If the command succeeded, surface those messages in `stdout` for clients.
    if rc == 0 and not out and err:
        out = err
        err = ''
    return make_response(rc, out, err)


@app.route("/api/pull", methods=["POST"])
def pull():
    """Pull from remote repository.

    Accepts optional JSON fields:
    - `remote` (default: 'origin')
    - `branch` (default: 'main')
    - `rebase` (boolean, default: False)
    - `extra_args` (list of additional flags)
    
    Token authentication uses environment variables (GITHUB_TOKEN, ADO_PAT) only.
    """
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    remote = data.get("remote", "origin")
    branch = data.get("branch", "main")
    rebase = bool(data.get("rebase", False))
    extra_args = data.get("extra_args")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    # Ensure extra_args is a list if provided
    if extra_args is not None and not isinstance(extra_args, list):
        return jsonify({"error": "extra_args must be a list"}), 400

    rc, out, err = runner.pull(repo_path, remote=remote, branch=branch, rebase=rebase, extra_args=extra_args)
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return make_response(rc, out, err)


@app.route("/api/push", methods=["POST"])
def push():
    """Push to remote repository.

    Accepts optional JSON fields:
    - `remote` (default: 'origin')
    - `branch` (default: 'main')
    - `extra_args` (list of additional flags)
    
    Token authentication uses environment variables (GITHUB_TOKEN, ADO_PAT) only.
    """
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    remote = data.get("remote", "origin")
    branch = data.get("branch", "main")
    extra_args = data.get("extra_args")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    # Ensure extra_args is a list if provided
    if extra_args is not None and not isinstance(extra_args, list):
        return jsonify({"error": "extra_args must be a list"}), 400

    rc, out, err = runner.push(repo_path, remote=remote, branch=branch, extra_args=extra_args)
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return make_response(rc, out, err)


@app.route('/api/commit', methods=['POST'])
def commit():
    data = request.get_json() or {}
    repo = data.get('repo_path')
    msg = data.get('message')
    if not repo or not os.path.exists(repo):
        return jsonify({'error': 'valid repo_path required'}), 400
    if not msg:
        return jsonify({'error': 'message (commit message) required'}), 400
    rc, out, err = runner.commit(repo, message=msg)
    commit_message = 'Commit successful' if rc == 0 else 'Commit failed'
    # Surface informational messages in stdout on success
    if rc == 0 and err:
        out = (out or '') + err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': commit_message})


@app.route('/api/run_safe', methods=['POST'])
def run_safe():
    data = request.get_json() or {}
    repo = data.get('repo_path')
    args = data.get('args')
    if not repo or not os.path.exists(repo):
        return jsonify({'error': 'valid repo_path required'}), 400
    if not isinstance(args, list):
        return jsonify({'error': 'args must be a list'}), 400
    rc, out, err = runner.run_safe(repo, args)
    return make_response(rc, out, err)


@app.route('/api/merge', methods=['POST'])
def merge():
    """Merge a branch into the current branch (git merge <branch>).

    Accepts JSON fields:
    - `branch` (required): Branch name to merge
    - `no_ff` (optional): Use --no-ff flag to create a merge commit
    - `extra_args` (optional): List of additional git merge arguments
    """
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    branch = data.get("branch")
    no_ff = bool(data.get("no_ff", False))
    extra_args = data.get("extra_args")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    if not branch:
        return jsonify({"error": "branch name is required"}), 400

    # Ensure extra_args is a list if provided
    if extra_args is not None and not isinstance(extra_args, list):
        return jsonify({"error": "extra_args must be a list"}), 400

    rc, out, err = runner.merge(repo_path, branch=branch, no_ff=no_ff, extra_args=extra_args)
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return make_response(rc, out, err)


@app.route('/api/stash', methods=['POST'])
def stash():
    """Git stash operations (list, save, pop, apply, drop, clear, show).

    Accepts JSON fields:
    - `action` (required): 'list', 'save', 'pop', 'apply', 'drop', 'clear', 'show'
    - `message` (for 'save'): stash message
    - `stash_index` (for 'pop', 'apply', 'drop', 'show'): stash identifier (e.g., 'stash@{0}')
    - `patch` (for 'show'): boolean, show as patch (default: false)
    """
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    action = data.get("action", "list")
    message = data.get("message")
    stash_index = data.get("stash_index")
    patch = bool(data.get("patch", False))

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    valid_actions = {'list', 'save', 'pop', 'apply', 'drop', 'clear', 'show'}
    if action not in valid_actions:
        return jsonify({"error": f"invalid action. must be one of: {', '.join(valid_actions)}"}), 400

    # Dispatch to appropriate method
    if action == 'list':
        rc, out, err = runner.stash_list(repo_path)
    elif action == 'save':
        rc, out, err = runner.stash_save(repo_path, message=message)
    elif action == 'pop':
        rc, out, err = runner.stash_pop(repo_path, stash_index=stash_index)
    elif action == 'apply':
        rc, out, err = runner.stash_apply(repo_path, stash_index=stash_index)
    elif action == 'drop':
        rc, out, err = runner.stash_drop(repo_path, stash_index=stash_index)
    elif action == 'clear':
        rc, out, err = runner.stash_clear(repo_path)
    elif action == 'show':
        rc, out, err = runner.stash_show(repo_path, stash_index=stash_index, patch=patch)

    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return make_response(rc, out, err)


@app.route('/api/reset', methods=['POST'])
def reset():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    mode = data.get("mode", "mixed")
    target = data.get("target")
    paths = data.get("paths")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    rc, out, err = runner.reset(repo_path, mode=mode, target=target, paths=paths)
    message = 'Reset successful' if rc == 0 else 'Reset failed'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/config', methods=['POST'])
def config_endpoint():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    action = data.get("action", "get")
    key = data.get("key")
    value = data.get("value")
    global_scope = bool(data.get("global_scope", False))

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    rc, out, err = runner.config(repo_path, action=action, key=key, value=value, global_scope=global_scope)
    message = f'Config {action} successful' if rc == 0 else f'Config {action} failed'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/restore', methods=['POST'])
def restore():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    paths = data.get("paths")
    source = data.get("source")
    staged = bool(data.get("staged", False))
    worktree = bool(data.get("worktree", False))

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400
    
    if not paths:
        return jsonify({"error": "paths parameter required (list of file paths)"}), 400

    rc, out, err = runner.restore(repo_path, paths=paths, source=source, staged=staged, worktree=worktree)
    message = 'Restore successful' if rc == 0 else 'Restore failed'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/conflict_status', methods=['POST'])
def conflict_status():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    rc, out, err = runner.conflict_status(repo_path)
    return make_response(rc, out, err)


@app.route('/api/show_conflicts', methods=['POST'])
def show_conflicts():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    file_path = data.get("file_path")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400
    
    if not file_path:
        return jsonify({"error": "file_path parameter required"}), 400

    rc, out, err = runner.show_conflicts(repo_path, file_path)
    message = 'File retrieved' if rc == 0 else 'Failed to retrieve file'
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/diff_conflict', methods=['POST'])
def diff_conflict():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    file_path = data.get("file_path")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    rc, out, err = runner.diff_conflict(repo_path, file_path=file_path)
    return make_response(rc, out, err)


@app.route('/api/abort_merge', methods=['POST'])
def abort_merge():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    rc, out, err = runner.abort_merge(repo_path)
    message = 'Merge/rebase aborted' if rc == 0 else 'Abort failed'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/merge_continue', methods=['POST'])
def merge_continue():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    message = data.get("message")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    rc, out, err = runner.merge_continue(repo_path, message=message)
    merge_msg = 'Merge completed' if rc == 0 else 'Merge completion failed'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': merge_msg})


@app.route('/api/rebase_continue', methods=['POST'])
def rebase_continue():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    rc, out, err = runner.rebase_continue(repo_path)
    message = 'Rebase continued' if rc == 0 else 'Rebase continuation failed'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/rebase_abort', methods=['POST'])
def rebase_abort():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")

    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400

    rc, out, err = runner.rebase_abort(repo_path)
    message = 'Rebase aborted' if rc == 0 else 'Rebase abort failed'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/show', methods=['POST'])
def show():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    commit = data.get("commit")
    
    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400
    if not commit:
        return jsonify({"error": "commit parameter required"}), 400
    
    rc, out, err = runner.show(repo_path, commit)
    message = 'Commit details retrieved' if rc == 0 else 'Failed to retrieve commit'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/diff', methods=['POST'])
def diff():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    ref1 = data.get("ref1")
    ref2 = data.get("ref2")
    file_path = data.get("file_path")
    
    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400
    
    rc, out, err = runner.diff(repo_path, ref1=ref1, ref2=ref2, file_path=file_path)
    message = 'Diff retrieved' if rc == 0 else 'Failed to retrieve diff'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/show_file', methods=['POST'])
def show_file():
    data = request.get_json() or {}
    repo_path = data.get("repo_path")
    commit = data.get("commit")
    file_path = data.get("file_path")
    
    if not repo_path or not os.path.exists(repo_path):
        return jsonify({"error": "valid repo_path required"}), 400
    if not commit:
        return jsonify({"error": "commit parameter required"}), 400
    if not file_path:
        return jsonify({"error": "file_path parameter required"}), 400
    
    rc, out, err = runner.show_file(repo_path, commit, file_path)
    message = 'File content retrieved' if rc == 0 else 'Failed to retrieve file content'
    
    # Surface informational stderr in stdout on success
    if rc == 0 and not out and err:
        out = err
        err = ''
    return jsonify({'returncode': rc, 'stdout': out, 'stderr': err, 'message': message})


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'git_path': config.get('git_path')})


def create_app(**kwargs):
    return app
