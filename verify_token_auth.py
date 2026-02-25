#!/usr/bin/env python3
"""
Token Authentication Verification Script

Run this script to verify that token authentication is properly configured
and working with your MCP Git Server.
"""

import os
import sys

def check_environment():
    """Check if required environment variables are set."""
    print("=" * 60)
    print("TOKEN AUTHENTICATION VERIFICATION")
    print("=" * 60)
    print()
    
    # Check Python environment
    print("1. Python Environment")
    print(f"   ✓ Python version: {sys.version.split()[0]}")
    print()
    
    # Check tokens
    print("2. Token Configuration")
    github_token = os.environ.get("GITHUB_TOKEN", "")
    ado_pat = os.environ.get("ADO_PAT", "")
    
    if github_token:
        masked = github_token[:7] + "..." + github_token[-4:] if len(github_token) > 11 else "***"
        print(f"   ✓ GITHUB_TOKEN: {masked}")
    else:
        print("   ✗ GITHUB_TOKEN: Not set")
    
    if ado_pat:
        masked = ado_pat[:4] + "..." + ado_pat[-4:] if len(ado_pat) > 8 else "***"
        print(f"   ✓ ADO_PAT: {masked}")
    else:
        print("   ✗ ADO_PAT: Not set")
    print()
    
    # Check credential-blocking variables
    print("3. Credential Blocking Variables")
    expected_vars = {
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ASKPASS": "true",
        "GCM_INTERACTIVE": "never",
    }
    
    for var, expected in expected_vars.items():
        value = os.environ.get(var, "")
        if value == expected:
            print(f"   ✓ {var}={value}")
        else:
            print(f"   ℹ {var}={value or '(not set)'} (will be auto-set by server)")
    print()
    
    # Test token injection
    print("4. Token Injection Test")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from mcp_git_server.git_tools import GitRunner
        
        runner = GitRunner(
            github_token=github_token,
            ado_pat=ado_pat
        )
        
        # Test GitHub URL
        test_gh_url = "https://github.com/user/repo.git"
        auth_gh_url = runner._auth_url(test_gh_url)
        if "x-access-token:" in auth_gh_url and github_token:
            print(f"   ✓ GitHub token injection: Working")
            print(f"     Format: https://x-access-token:***@github.com/...")
        elif not github_token:
            print(f"   ℹ GitHub token injection: Skipped (no token set)")
        else:
            print(f"   ✗ GitHub token injection: Failed")
        
        # Test ADO URL
        test_ado_url = "https://dev.azure.com/org/project/_git/repo"
        auth_ado_url = runner._auth_url(test_ado_url)
        if "PAT:" in auth_ado_url and ado_pat:
            print(f"   ✓ ADO token injection: Working")
            print(f"     Format: https://PAT:***@dev.azure.com/...")
        elif not ado_pat:
            print(f"   ℹ ADO token injection: Skipped (no token set)")
        else:
            print(f"   ✗ ADO token injection: Failed")
        
    except ImportError as e:
        print(f"   ✗ Cannot import GitRunner: {e}")
        print(f"     Make sure you're running from the mcp-git-server directory")
    print()
    
    # Configuration suggestions
    print("5. Configuration Recommendations")
    if not github_token and not ado_pat:
        print("   ⚠ No tokens configured!")
        print("     Set tokens in your mcp.json or environment:")
        print()
        print("     export GITHUB_TOKEN=ghp_your_token")
        print("     export ADO_PAT=your_ado_token")
    elif github_token and not ado_pat:
        print("   ℹ Only GitHub token configured (OK if not using Azure DevOps)")
    elif ado_pat and not github_token:
        print("   ℹ Only ADO token configured (OK if not using GitHub)")
    else:
        print("   ✓ Both tokens configured")
    print()
    
    # Final summary
    print("=" * 60)
    if (github_token or ado_pat):
        print("STATUS: ✓ Token authentication is configured")
        print()
        print("Next steps:")
        print("1. Start the server: python run_server.py")
        print("2. Configure tokens in VS Code mcp.json")
        print("3. Test with Copilot: 'Pull my private repo'")
    else:
        print("STATUS: ⚠ Token authentication not configured")
        print()
        print("Next steps:")
        print("1. Create GitHub token: https://github.com/settings/tokens")
        print("2. Create ADO token: https://dev.azure.com")
        print("3. Add tokens to mcp.json (see mcp.json.example)")
        print("4. Restart VS Code")
    print("=" * 60)

if __name__ == "__main__":
    check_environment()
