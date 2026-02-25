import subprocess
import shlex
import os
import time
import platform
from typing import Tuple, List


class GitRunner:
    """Git command runner with token authentication and cross-platform credential management.
    
    This class provides methods to execute git commands with automatic token injection
    for GitHub and Azure DevOps, credential prompt blocking, and timeout management.
    """
    
    def __init__(self, git_path="/usr/bin/git", github_token="", ado_pat="", timeout: int = 30):
        """Initialize GitRunner with git executable path and authentication tokens.
        
        Args:
            git_path: Path to git executable (default: /usr/bin/git)
            github_token: GitHub Personal Access Token for authentication
            ado_pat: Azure DevOps Personal Access Token for authentication
            timeout: Default timeout in seconds for git operations (default: 30)
        """
        self.git_path = git_path
        self.github_token = github_token
        self.ado_pat = ado_pat
        self.timeout = int(timeout or 30)
    
    def _auth_url(self, repo_url: str) -> str:
        """Return an authenticated URL with token injection for GitHub or Azure DevOps.
        
        Injects the appropriate token into HTTPS URLs for GitHub (using x-access-token)
        or Azure DevOps (using PAT). Non-HTTP URLs (e.g., SSH) are left unchanged.
        
        Args:
            repo_url: Repository URL (HTTP/HTTPS or SSH)
        
        Returns:
            Authenticated URL string with token injected, or original URL if not HTTP
        """
        if not isinstance(repo_url, str) or not repo_url.startswith('http'):
            return repo_url

        # strip scheme and any existing username@
        scheme = 'https://'
        url = repo_url
        if url.startswith(scheme):
            url = url[len(scheme):]
        if '@' in url:
            url = url.split('@', 1)[-1]

        if 'github.com' in url and self.github_token:
            # GitHub prefers x-access-token as username for PATs
            return f"{scheme}x-access-token:{self.github_token}@{url}"
        if ('dev.azure.com' in url or 'visualstudio.com' in url) and self.ado_pat:
            # ADO accepts PAT directly as username (any value works, PAT is the key)
            return f"{scheme}PAT:{self.ado_pat}@{url}"
        return repo_url

    def _run(self, args: List[str], cwd: str = None, repo_url: str = None, timeout: int = None) -> Tuple[int, str, str]:
        """Execute a git command with credential blocking and automatic token authentication.
        
        For remote operations (pull/push/fetch), automatically detects the repository URL
        from git remote, temporarily replaces the origin URL with an authenticated version,
        executes the command, and restores the original URL afterward. All credential prompts
        are blocked across platforms (macOS, Linux, Windows).
        
        Args:
            args: List of git command arguments (e.g., ['status', '--porcelain'])
            cwd: Working directory for the git command (typically repo path)
            repo_url: Repository URL for authentication (auto-detected if not provided)
            timeout: Command timeout in seconds (uses instance default if None)
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
            - returncode: Git command exit code (0 for success, non-zero for errors)
            - stdout: Standard output from the git command
            - stderr: Standard error output from the git command
        """
        env = os.environ.copy()
        
        # Disable all credential prompts on ALL platforms (macOS, Linux, Windows)
        # This ensures git uses the injected token and never prompts for credentials
        env["GIT_TERMINAL_PROMPT"] = "0"  # Disable terminal credential prompts
        env["GIT_ASKPASS"] = "true"        # Disable askpass credential helper (use 'true' command which returns success but does nothing)
        env["GCM_INTERACTIVE"] = "never"   # Disable Git Credential Manager interactive mode
        env["GIT_TRACE"] = "0"             # Disable git tracing for cleaner output
        
        # Additional Windows-specific settings
        if platform.system() == "Windows":
            env["GCM_PROVIDER"] = "generic"  # Use generic provider, not Windows Credential Manager
        
        cmd = [self.git_path] + list(args)
        orig_remote = None
        should_restore = False
        debug = os.environ.get("GIT_RUNNER_DEBUG") == "1"

        # effective timeout (None -> use configured default)
        timeout = int(timeout) if timeout is not None else int(self.timeout)

        cmd_str = ' '.join(args)
        if debug:
            print(f"[GIT_DEBUG] Starting: {cmd_str} (timeout={timeout}s)", flush=True)
            start_time = time.time()

        try:
            # For remote operations (pull/push/fetch), detect and inject token auth
            if cwd and os.path.isdir(cwd) and args and args[0] in ('pull', 'push', 'fetch'):
                if debug:
                    print(f"[GIT_DEBUG] Remote operation detected: {args[0]}", flush=True)
                
                # If repo_url not provided, fetch it from git remote
                if not repo_url:
                    if debug:
                        print(f"[GIT_DEBUG] Detecting repo_url from git remote...", flush=True)
                    try:
                        p = subprocess.run([self.git_path, 'remote', 'get-url', 'origin'], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=5)
                        if p.returncode == 0:
                            repo_url = p.stdout.strip()
                            if debug:
                                print(f"[GIT_DEBUG] Detected repo_url: {repo_url}", flush=True)
                    except Exception as e:
                        if debug:
                            print(f"[GIT_DEBUG] Failed to detect repo_url: {e}", flush=True)
                        repo_url = None

                # If we have a repo URL, inject token auth
                if repo_url:
                    # Get and save original origin URL
                    try:
                        p = subprocess.run([self.git_path, 'remote', 'get-url', 'origin'], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=5)
                        if p.returncode == 0:
                            orig_remote = p.stdout.strip()
                    except Exception:
                        orig_remote = None

                    auth_url = self._auth_url(repo_url)
                    if auth_url:
                        if debug:
                            print(f"[GIT_DEBUG] Injecting token auth...", flush=True)
                        # set new origin with token auth
                        subprocess.run([self.git_path, 'remote', 'set-url', 'origin', auth_url], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=5)
                        should_restore = orig_remote is not None

            if debug:
                print(f"[GIT_DEBUG] Executing: {cmd_str}", flush=True)
            
            proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, text=True, env=env)
            
            if debug:
                elapsed = time.time() - start_time
                print(f"[GIT_DEBUG] Completed in {elapsed:.2f}s (rc={proc.returncode})", flush=True)
                if proc.stderr:
                    print(f"[GIT_DEBUG] stderr: {proc.stderr[:200]}", flush=True)
            
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            if debug:
                elapsed = time.time() - start_time
                print(f"[GIT_DEBUG] TIMEOUT after {elapsed:.2f}s (configured timeout={timeout}s)", flush=True)
            return 124, '', f'Timeout after {timeout}s'
        except FileNotFoundError:
            return 127, '', f'git executable not found: {self.git_path}'
        except Exception as e:
            if debug:
                print(f"[GIT_DEBUG] Exception: {e}", flush=True)
            return 1, '', str(e)
        finally:
            # restore remote if we changed it
            if should_restore and orig_remote is not None and cwd and os.path.isdir(cwd):
                try:
                    if debug:
                        print(f"[GIT_DEBUG] Restoring original remote URL...", flush=True)
                    subprocess.run([self.git_path, 'remote', 'set-url', 'origin', orig_remote], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=5)
                except Exception:
                    pass

    def clone(self, repo_url: str, dest: str = None, extra_args: List[str] = None) -> Tuple[int, str, str]:
        """Clone a repository with automatic token authentication.
        
        Clones a Git repository using the appropriate authentication token (GitHub or Azure DevOps).
        If the destination exists as a directory, the repo is cloned into a subfolder named after
        the repository. Otherwise, the destination is used as the exact target path.
        
        Args:
            repo_url: Repository URL to clone (HTTP/HTTPS or SSH)
            dest: Destination directory path (creates subfolder if dest exists)
            extra_args: Additional git clone arguments (e.g., ['--depth', '1', '--branch', 'main'])
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        final_dest = dest
        
        # If dest exists and is a directory, extract repo name and use as subfolder
        if dest and os.path.isdir(dest):
            # Extract repo name from URL (last part, strip .git)
            repo_name = repo_url.rstrip('/').split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            final_dest = os.path.join(dest, repo_name)
        
        # Apply token authentication
        auth_url = self._auth_url(repo_url)
        
        args = ['clone', auth_url]
        if final_dest:
            args.append(final_dest)
        if extra_args:
            args += extra_args
        return self._run(args)

    def status(self, repo_path: str, human: bool = True) -> Tuple[int, str, str]:
        """Get repository status in human-readable or machine-readable format.
        
        Returns the current working tree status, including modified files, staged changes,
        and branch information. The output format can be human-readable or porcelain.
        
        Args:
            repo_path: Path to the git repository
            human: If True, returns human-readable output; if False, returns porcelain v2 format
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        if human:
            return self._run(['status'], cwd=repo_path)
        return self._run(['status', '--porcelain=2', '-b'], cwd=repo_path)

    def log(self, repo_path: str, n: int = 20) -> Tuple[int, str, str]:
        """Get commit history in oneline format.
        
        Retrieves the most recent commit logs with each commit displayed on a single line
        showing the commit hash and message.
        
        Args:
            repo_path: Path to the git repository
            n: Number of commits to retrieve (default: 20)
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        return self._run(['log', f'-n{n}', '--pretty=oneline'], cwd=repo_path)

    def branch(self, repo_path: str) -> Tuple[int, str, str]:
        """Get the current branch name.
        
        Returns the name of the currently checked out branch. If in detached HEAD state,
        returns an empty string.
        
        Args:
            repo_path: Path to the git repository
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
            stdout contains the current branch name
        """
        return self._run(['branch', '--show-current'], cwd=repo_path)

    def fetch(self, repo_path: str, remote: str = None, branch: str = None, repo_url: str = None) -> Tuple[int, str, str]:
        """Fetch updates from a remote repository with token authentication.
        
        Downloads objects and refs from the remote repository without merging.
        Can optionally fetch a specific branch from a specific remote.
        
        Args:
            repo_path: Path to the git repository
            remote: Remote name (e.g., 'origin'); if None, uses default remote
            branch: Specific branch to fetch; if None, fetches all branches
            repo_url: Repository URL for token authentication (auto-detected if None)
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        args = ['fetch']
        if remote:
            args.append(remote)
        if branch:
            # fetch specific branch from remote
            args.append(branch)
        return self._run(args, cwd=repo_path, repo_url=repo_url)
    
    def checkout(self, repo_path: str, target: str = None, create: bool = False) -> Tuple[int, str, str]:
        """Checkout a branch or commit, optionally creating a new branch.
        
        Switches the working directory to the specified branch or commit.
        Can create a new branch with the create flag.
        
        Args:
            repo_path: Path to the git repository
            target: Branch name or commit hash to checkout (required)
            create: If True, creates a new branch and checks it out (git checkout -b)
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        if not target:
            return 1, '', 'target (branch or commit) is required'
        if create:
            return self._run(['checkout', '-b', target], cwd=repo_path)
        return self._run(['checkout', target], cwd=repo_path)

    def add(self, repo_path: str, paths=None) -> Tuple[int, str, str]:
        """Add files to the staging area (index).
        
        Stages changes for the next commit. Accepts flexible path specifications.
        
        Args:
            repo_path: Path to the git repository
            paths: Files to add:
                - None: stages all changes (equivalent to 'git add .')
                - str: single file path or pathspec
                - List[str]: multiple file paths or pathspecs
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        if not repo_path or not os.path.isdir(repo_path):
            return 1, '', 'invalid repo_path'
        args = ['add']
        if paths is None:
            args.append('.')
        elif isinstance(paths, list):
            args += [str(p) for p in paths]
        else:
            args.append(str(paths))
        return self._run(args, cwd=repo_path)

    def pull(self, repo_path: str, remote: str = 'origin', branch: str = 'main', rebase: bool = False, extra_args: List[str] = None) -> Tuple[int, str, str]:
        """Pull changes from a remote repository with token authentication.
        
        Fetches and integrates changes from the remote branch into the current branch.
        Supports rebase mode and additional git flags.
        
        Args:
            repo_path: Path to the git repository
            remote: Remote name (default: 'origin')
            branch: Branch name to pull (default: 'main')
            rebase: If True, uses rebase instead of merge (--rebase flag)
            extra_args: Additional git pull arguments (e.g., ['--no-ff', '--verbose'])
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        args = ['pull']
        # add remote/branch first so flags like --rebase can appear after
        if remote:
            args.append(remote)
        if branch:
            args.append(branch)
        if extra_args:
            args += extra_args
        # place rebase flag after branch/extra args to support
        # `git pull origin feature/foo --rebase`
        if rebase:
            args.append('--rebase')
        return self._run(args, cwd=repo_path, repo_url=None)

    def push(self, repo_path: str, remote: str = 'origin', branch: str = 'main', extra_args: List[str] = None) -> Tuple[int, str, str]:
        """Push local commits to a remote repository with token authentication.
        
        Uploads local branch commits to the remote repository. Token authentication
        is automatically applied based on GITHUB_TOKEN or ADO_PAT configuration.
        
        Args:
            repo_path: Path to the git repository
            remote: Remote name (default: 'origin')
            branch: Branch name to push (default: 'main')
            extra_args: Additional git push arguments (e.g., ['--force-with-lease', '--tags'])
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        args = ['push', remote, branch]
        if extra_args:
            args += extra_args
        return self._run(args, cwd=repo_path, repo_url=None)

    def commit(self, repo_path: str, message: str = None) -> Tuple[int, str, str]:
        """Create a commit with staged changes.
        
        Records staged changes to the repository with the provided commit message.
        
        Args:
            repo_path: Path to the git repository
            message: Commit message (required)
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        if not message:
            return 1, '', 'commit message is required'
        return self._run(['commit', '-m', message], cwd=repo_path)

    def merge(self, repo_path: str, branch: str = None, no_ff: bool = False, extra_args: List[str] = None) -> Tuple[int, str, str]:
        """Merge a branch into the current branch.
        
        Integrates changes from the specified branch into the current branch.
        Can force creation of a merge commit for better history visualization.
        
        Args:
            repo_path: Path to the git repository
            branch: Branch name to merge into the current branch (required)
            no_ff: If True, creates a merge commit even for fast-forward merges (--no-ff)
            extra_args: Additional git merge arguments (e.g., ['--squash', '--no-commit'])
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
            returncode will be non-zero if merge conflicts occur
        """
        if not branch:
            return 1, '', 'branch name is required for merge'
        
        args = ['merge']
        if no_ff:
            args.append('--no-ff')
        args.append(branch)
        if extra_args:
            args += extra_args
        
        return self._run(args, cwd=repo_path)

    def stash_list(self, repo_path: str) -> Tuple[int, str, str]:
        """List all saved stashes.
        
        Displays all stashed changes with their indices and descriptions.
        
        Args:
            repo_path: Path to the git repository
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
            stdout contains list of stashes in format 'stash@{N}: <message>'
        """
        return self._run(['stash', 'list'], cwd=repo_path)

    def stash_save(self, repo_path: str, message: str = None) -> Tuple[int, str, str]:
        """Save current working directory changes to a new stash.
        
        Stores uncommitted changes (both staged and unstaged) in a stash,
        and reverts the working directory to match the HEAD commit.
        
        Args:
            repo_path: Path to the git repository
            message: Optional description for the stash
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        args = ['stash', 'push']
        if message:
            args.extend(['-m', message])
        return self._run(args, cwd=repo_path)

    def stash_apply(self, repo_path: str, stash_index: str = None) -> Tuple[int, str, str]:
        """Apply a stashed change without removing it from the stash list.
        
        Reapplies changes from a stash to the working directory. The stash
        remains in the stash list for potential reuse.
        
        Args:
            repo_path: Path to the git repository
            stash_index: Stash reference (e.g., 'stash@{0}'); if None, applies most recent stash
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        args = ['stash', 'apply']
        if stash_index:
            args.append(stash_index)
        return self._run(args, cwd=repo_path)

    def stash_pop(self, repo_path: str, stash_index: str = None) -> Tuple[int, str, str]:
        """Apply a stash and remove it from the stash list.
        
        Reapplies changes from a stash to the working directory, then removes
        that stash from the list. If conflicts occur, the stash is not removed.
        
        Args:
            repo_path: Path to the git repository
            stash_index: Stash reference (e.g., 'stash@{0}'); if None, pops most recent stash
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        args = ['stash', 'pop']
        if stash_index:
            args.append(stash_index)
        return self._run(args, cwd=repo_path)

    def stash_drop(self, repo_path: str, stash_index: str = None) -> Tuple[int, str, str]:
        """Remove a single stash from the stash list.
        
        Permanently deletes a stash without applying it. Use with caution
        as deleted stashes cannot be recovered easily.
        
        Args:
            repo_path: Path to the git repository
            stash_index: Stash reference (e.g., 'stash@{0}'); if None, drops most recent stash
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        args = ['stash', 'drop']
        if stash_index:
            args.append(stash_index)
        return self._run(args, cwd=repo_path)

    def stash_clear(self, repo_path: str) -> Tuple[int, str, str]:
        """Remove all stashes from the repository.
        
        Permanently deletes all stashed changes. This operation cannot be undone,
        so use with extreme caution.
        
        Args:
            repo_path: Path to the git repository
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        return self._run(['stash', 'clear'], cwd=repo_path)

    def stash_show(self, repo_path: str, stash_index: str = None, patch: bool = False) -> Tuple[int, str, str]:
        """Display the contents of a stash.
        
        Shows the changes stored in a stash. Can display as a summary of changed files
        or as a full patch diff.
        
        Args:
            repo_path: Path to the git repository
            stash_index: Stash reference (e.g., 'stash@{0}'); if None, shows most recent stash
            patch: If True, shows full diff patch (-p flag); if False, shows summary
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        """
        args = ['stash', 'show']
        if stash_index:
            args.append(stash_index)
        if patch:
            args.append('-p')
        return self._run(args, cwd=repo_path)

    def reset(self, repo_path: str, mode: str = 'mixed', target: str = None, paths: List[str] = None) -> Tuple[int, str, str]:
        """Reset current HEAD to a specified state.
        
        Moves the HEAD pointer and optionally modifies the index and working directory.
        Can also be used to unstage specific files.
        
        Args:
            repo_path: Path to the git repository
            mode: Reset mode - 'soft', 'mixed', 'hard', 'merge', or 'keep' (default: 'mixed')
            target: Commit hash, branch name, or ref to reset to (e.g., 'HEAD~1', 'origin/main')
            paths: List of file paths to reset (unstage). When provided, mode is ignored
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        
        Note:
            - 'soft': Move HEAD only, keep index and working directory unchanged
            - 'mixed': Move HEAD and reset index, keep working directory unchanged (default)
            - 'hard': Move HEAD, reset index and working directory (DESTRUCTIVE)
            - When paths are specified, only those files are unstaged
        """
        if paths:
            # Unstage specific files (git reset -- <paths>)
            args = ['reset', '--']
            args.extend(paths)
            return self._run(args, cwd=repo_path)
        
        # Full reset with mode
        args = ['reset']
        valid_modes = {'soft', 'mixed', 'hard', 'merge', 'keep'}
        if mode not in valid_modes:
            return 1, '', f'Invalid reset mode: {mode}. Valid modes: {", ".join(valid_modes)}'
        
        args.append(f'--{mode}')
        if target:
            args.append(target)
        
        return self._run(args, cwd=repo_path)

    def config(self, repo_path: str, action: str = 'get', key: str = None, value: str = None, global_scope: bool = False) -> Tuple[int, str, str]:
        """Get, set, or list git configuration values.
        
        Manages git configuration at repository or global level. Can read individual
        config values, set new values, or list all configuration.
        
        Args:
            repo_path: Path to the git repository (required even for global config)
            action: Operation to perform - 'get', 'set', 'unset', or 'list' (default: 'get')
            key: Configuration key (e.g., 'user.name', 'core.editor')
            value: Value to set (required when action is 'set')
            global_scope: If True, operates on global config; if False, repository config
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
            For 'get': stdout contains the config value
            For 'list': stdout contains all configuration in 'key=value' format
        
        Note:
            Common config keys: user.name, user.email, core.editor, core.autocrlf
        """
        if action not in {'get', 'set', 'unset', 'list'}:
            return 1, '', f'Invalid action: {action}. Valid actions: get, set, unset, list'
        
        args = ['config']
        if global_scope:
            args.append('--global')
        
        if action == 'list':
            args.append('--list')
        elif action == 'get':
            if not key:
                return 1, '', 'key is required for get action'
            args.append('--get')
            args.append(key)
        elif action == 'set':
            if not key or value is None:
                return 1, '', 'key and value are required for set action'
            args.append(key)
            args.append(value)
        elif action == 'unset':
            if not key:
                return 1, '', 'key is required for unset action'
            args.append('--unset')
            args.append(key)
        
        return self._run(args, cwd=repo_path)

    def restore(self, repo_path: str, paths: List[str] = None, source: str = None, staged: bool = False, worktree: bool = False) -> Tuple[int, str, str]:
        """Restore working tree files or unstage changes.
        
        Modern Git command (2.23+) to restore files in the working directory or staging area.
        This is the preferred alternative to 'git checkout' for file operations.
        
        Args:
            repo_path: Path to the git repository
            paths: List of file paths to restore (required)
            source: Source to restore from (e.g., 'HEAD', 'HEAD~1', branch name)
            staged: If True, restores files in the staging area (--staged flag)
            worktree: If True, restores files in the working tree (--worktree flag, default behavior)
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
        
        Note:
            - Default behavior: restore working tree from index
            - Use staged=True to unstage files (restore index from HEAD)
            - Use both staged=True and worktree=True to discard all changes
        """
        if not paths:
            return 1, '', 'paths parameter is required (list of file paths to restore)'
        
        args = ['restore']
        
        if staged:
            args.append('--staged')
        if worktree:
            args.append('--worktree')
        
        if source:
            args.extend(['--source', source])
        
        args.append('--')
        if isinstance(paths, list):
            args.extend(paths)
        else:
            args.append(str(paths))
        
        return self._run(args, cwd=repo_path)

    def run_safe(self, repo_path: str, args: List[str]) -> Tuple[int, str, str]:
        """Execute a safe read-only git command.
        
        Runs only whitelisted git commands that are read-only and cannot modify
        the repository state. This is useful for executing arbitrary git queries
        while preventing destructive operations.
        
        Args:
            repo_path: Path to the git repository
            args: Git command arguments (first element must be in safe commands list)
        
        Returns:
            Tuple of (returncode: int, stdout: str, stderr: str)
            Returns error if command is not in the safe list
        
        Note:
            Allowed commands: status, log, branch, show, diff
        """
        # Only allow specific safe subcommands; block arbitrary flags that could be harmful
        safe_cmds = {'status', 'log', 'branch', 'show', 'diff'}
        if not args:
            return 1, '', 'No arguments provided'
        if args[0] not in safe_cmds:
            return 1, '', f'Command `{args[0]}` not allowed via run_safe'
        return self._run(args, cwd=repo_path)
