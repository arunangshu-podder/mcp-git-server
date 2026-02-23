import os
import yaml

def load_config(config_file="config.yml"):
    """Load configuration from YAML file and environment variables."""
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    # Resolve environment variable references (${VAR_NAME})
    def resolve_env(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            var_name = value[2:-1]
            return os.getenv(var_name, "")
        return value
    
    git_path = resolve_env(config.get("git", {}).get("path", "/usr/bin/git"))
    github_token = resolve_env(config.get("auth", {}).get("github_token", ""))
    ado_pat = resolve_env(config.get("auth", {}).get("ado_pat", ""))
    # timeout in seconds (env overrides YAML)
    timeout_val = config.get('timeout', None)
    timeout = int(os.environ.get('GIT_TIMEOUT', timeout_val if timeout_val is not None else 30))
    
    return {
        "git_path": git_path,
        "github_token": github_token,
        "ado_pat": ado_pat,
        "timeout": timeout,
    }