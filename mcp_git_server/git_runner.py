import subprocess
import shlex
import os
from typing import Tuple, List


class GitRunner:
    def __init__(self, git_path="/usr/bin/git", github_token="", ado_pat="", timeout: int = 30):
        self.git_path = git_path
        self.github_token = github_token
        self.ado_pat = ado_pat
        self.timeout = int(timeout or 30)
    
    def _auth_url(self, repo_url: str) -> str:
        """Return an authenticated URL (inject token) for GitHub or ADO if configured.

        Leaves non-HTTP URLs unchanged.
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
            return f"{scheme}git:{self.github_token}@{url}"
        if ('dev.azure.com' in url or 'visualstudio.com' in url) and self.ado_pat:
            return f"{scheme}PAT:{self.ado_pat}@{url}"
        return repo_url

    def _run(self, args: List[str], cwd: str = None, repo_url: str = None, timeout: int = None) -> Tuple[int, str, str]:
        """Run a git command (args as list). If `repo_url` is provided for operations
        that touch a remote (pull/push/fetch), temporarily set `origin` to the
        authenticated URL and restore it afterward.
        Returns (returncode, stdout, stderr).
        """
        env = os.environ.copy()
        cmd = [self.git_path] + list(args)
        orig_remote = None
        should_restore = False

        # effective timeout (None -> use configured default)
        timeout = int(timeout) if timeout is not None else int(self.timeout)

        try:
            # If repo_url provided and cwd exists and command touches remote, swap origin
            if repo_url and cwd and os.path.isdir(cwd) and args and args[0] in ('pull', 'push', 'fetch'):
                # attempt to read original origin URL
                try:
                    p = subprocess.run([self.git_path, 'remote', 'get-url', 'origin'], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
                    if p.returncode == 0:
                        orig_remote = p.stdout.strip()
                except Exception:
                    orig_remote = None

                auth_url = self._auth_url(repo_url)
                if auth_url:
                    # set new origin
                    subprocess.run([self.git_path, 'remote', 'set-url', 'origin', auth_url], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
                    should_restore = orig_remote is not None

            proc = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, text=True, env=env)
            return proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            return 124, '', f'Timeout after {timeout}s'
        except FileNotFoundError:
            return 127, '', f'git executable not found: {self.git_path}'
        except Exception as e:
            return 1, '', str(e)
        finally:
            # restore remote if we changed it
            if should_restore and orig_remote is not None and cwd and os.path.isdir(cwd):
                try:
                    subprocess.run([self.git_path, 'remote', 'set-url', 'origin', orig_remote], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
                except Exception:
                    pass

    def clone(self, repo_url: str, dest: str = None, extra_args: List[str] = None) -> Tuple[int, str, str]:
        """Clone a repository with token authentication.
        
        If `dest` already exists as a directory, clone into a subfolder using the repo name.
        Otherwise, use `dest` as the target directory path.
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
        """Get repository status.

        If `human` is True, returns the same output as `git status`.
        Otherwise returns machine-readable porcelain output used by tools.
        """
        if human:
            return self._run(['status'], cwd=repo_path)
        return self._run(['status', '--porcelain=2', '-b'], cwd=repo_path)

    def log(self, repo_path: str, n: int = 20) -> Tuple[int, str, str]:
        return self._run(['log', f'-n{n}', '--pretty=oneline'], cwd=repo_path)

    def branch(self, repo_path: str) -> Tuple[int, str, str]:
        return self._run(['branch', '--show-current'], cwd=repo_path)

    def fetch(self, repo_path: str, remote: str = None, branch: str = None, repo_url: str = None) -> Tuple[int, str, str]:
        """Fetch from remote. Optionally fetch a specific branch.

        If `repo_url` is provided it will be used for token-auth when contacting the remote.
        """
        args = ['fetch']
        if remote:
            args.append(remote)
        if branch:
            # fetch specific branch from remote
            args.append(branch)
        return self._run(args, cwd=repo_path, repo_url=repo_url)
    
    def checkout(self, repo_path: str, target: str = None, create: bool = False) -> Tuple[int, str, str]:
        """Checkout a branch or commit.

        Args:
            repo_path: Path to the repository
            target: Branch name or commit hash to checkout
            create: if True, run `git checkout -b <target>` to create the branch
        """
        if not target:
            return 1, '', 'target (branch or commit) is required'
        if create:
            return self._run(['checkout', '-b', target], cwd=repo_path)
        return self._run(['checkout', target], cwd=repo_path)

    def add(self, repo_path: str, paths=None) -> Tuple[int, str, str]:
        """Add files to index.

        `paths` may be:
        - None -> equivalent to `git add .`
        - a string -> a single pathspec (file or '.')
        - a list of strings -> multiple pathspecs
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

    def pull(self, repo_path: str, repo_url: str = None, remote: str = 'origin', branch: str = 'main', rebase: bool = False, extra_args: List[str] = None) -> Tuple[int, str, str]:
        """Pull from remote (with token auth if repo_url provided).

        Supports `rebase=True` to run `git pull --rebase`.
        `extra_args` may be provided as a list of additional flags.
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
        return self._run(args, cwd=repo_path, repo_url=repo_url)

    def push(self, repo_path: str, repo_url: str = None, remote: str = 'origin', branch: str = 'main') -> Tuple[int, str, str]:
        """Push to remote (optionally using `repo_url` for token auth)."""
        return self._run(['push', remote, branch], cwd=repo_path, repo_url=repo_url)

    def commit(self, repo_path: str, message: str = None) -> Tuple[int, str, str]:
        """Commit staged changes.

        Args:
            repo_path: Path to the repository
            message: Commit message (required)
        """
        if not message:
            return 1, '', 'commit message is required'
        return self._run(['commit', '-m', message], cwd=repo_path)

    def run_safe(self, repo_path: str, args: List[str]) -> Tuple[int, str, str]:
        # Only allow specific safe subcommands; block arbitrary flags that could be harmful
        safe_cmds = {'status', 'log', 'branch', 'show', 'diff'}
        if not args:
            return 1, '', 'No arguments provided'
        if args[0] not in safe_cmds:
            return 1, '', f'Command `{args[0]}` not allowed via run_safe'
        return self._run(args, cwd=repo_path)
