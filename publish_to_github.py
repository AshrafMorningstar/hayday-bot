#!/usr/bin/env python3
"""
publish_to_github.py
====================
Fully automated dual-repository creator and publisher for inxernal.
Publishes:
  1. Private Repository (Full source code, native engine, tests, architecture docs)
  2. Public Repository (Clean client distribution, automated setup, public Quick Start guide)

Usage:
  python publish_to_github.py
  python publish_to_github.py --token <GITHUB_PAT>
  python publish_to_github.py --private-name inxernal-core --public-name inxernal
"""

import sys
import os
import subprocess
import shutil
import argparse
from pathlib import Path

# Fix Windows console ANSI
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_RED    = "\033[91m"
C_CYAN   = "\033[96m"
C_MAGENTA= "\033[95m"

def log_info(msg):
    print(f"{C_CYAN}[*]{C_RESET} {msg}")

def log_success(msg):
    print(f"{C_GREEN}[+]{C_RESET} {C_BOLD}{msg}{C_RESET}")

def log_warn(msg):
    print(f"{C_YELLOW}[!]{C_RESET} {msg}")

def log_error(msg):
    print(f"{C_RED}[-]{C_RESET} {C_BOLD}{msg}{C_RESET}")

def find_executable(name, extra_paths=None):
    cmd = shutil.which(name)
    if cmd:
        return cmd
    if extra_paths:
        for p in extra_paths:
            candidate = Path(p)
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)
    return None

def run_cmd(cmd, cwd=None, check=True, capture=True):
    log_info(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture,
        text=True,
        shell=isinstance(cmd, str)
    )
    if check and res.returncode != 0:
        err = res.stderr.strip() if res.stderr else res.stdout.strip()
        raise RuntimeError(f"Command failed ({res.returncode}): {err}")
    return res

def get_git_path():
    extra = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\bin\git.exe")
    ]
    path = find_executable("git", extra)
    if not path:
        raise RuntimeError("Git is not installed or not found in PATH.")
    return path

def get_gh_path():
    extra = [
        r"C:\Program Files\GitHub CLI\gh.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\GitHub CLI\gh.exe")
    ]
    path = find_executable("gh", extra)
    if not path:
        raise RuntimeError("GitHub CLI (gh) is not installed or not found in PATH.")
    return path

def check_auth(gh_bin, token=None):
    if token:
        log_info("Authenticating with provided GitHub token...")
        p = subprocess.run(
            [gh_bin, "auth", "login", "--with-token"],
            input=token,
            text=True,
            capture_output=True
        )
        if p.returncode != 0:
            raise RuntimeError(f"Token authentication failed: {p.stderr.strip()}")
        log_success("Authenticated successfully using token!")
        return True

    # Check existing auth
    res = subprocess.run([gh_bin, "auth", "status"], capture_output=True, text=True)
    if res.returncode == 0:
        log_success("GitHub CLI is already authenticated.")
        return True

    print(f"\n{C_YELLOW}GitHub authentication required.{C_RESET}")
    print("Choose an option:")
    print("  [1] Web browser login (easiest)")
    print("  [2] Enter GitHub Personal Access Token (PAT)")
    print("  [3] Exit")

    choice = input(f"{C_BOLD}Select [1/2/3] (default 1): {C_RESET}").strip() or "1"
    if choice == "1":
        log_info("Launching browser authentication...")
        res = subprocess.run([gh_bin, "auth", "login", "-h", "github.com", "-p", "https", "-w"])
        if res.returncode != 0:
            raise RuntimeError("Browser login was cancelled or failed.")
        log_success("Browser authentication complete!")
        return True
    elif choice == "2":
        tok = input("Enter Personal Access Token: ").strip()
        if not tok:
            raise RuntimeError("No token provided.")
        return check_auth(gh_bin, token=tok)
    else:
        sys.exit(0)

def get_github_username(gh_bin):
    res = run_cmd([gh_bin, "api", "user", "-q", ".login"])
    user = res.stdout.strip()
    if not user:
        raise RuntimeError("Could not determine GitHub username.")
    return user

def init_local_git(git_bin, repo_root, username):
    dot_git = repo_root / ".git"
    if not dot_git.exists():
        log_info("Initializing local git repository...")
        run_cmd([git_bin, "init", "-b", "main"], cwd=repo_root)

    # Configure user.name and user.email if missing
    try:
        run_cmd([git_bin, "config", "user.name"], cwd=repo_root)
    except Exception:
        run_cmd([git_bin, "config", "user.name", username], cwd=repo_root)
    try:
        run_cmd([git_bin, "config", "user.email"], cwd=repo_root)
    except Exception:
        run_cmd([git_bin, "config", "user.email", f"{username}@users.noreply.github.com"], cwd=repo_root)

    # Add all files (ignoring files in .gitignore)
    log_info("Staging workspace files...")
    run_cmd([git_bin, "add", "."], cwd=repo_root)

    # Check if there is anything to commit
    status_res = run_cmd([git_bin, "status", "--porcelain"], cwd=repo_root)
    if status_res.stdout.strip():
        log_info("Committing workspace files...")
        run_cmd([
            git_bin, "commit", "-m",
            "feat: initial release with autonomous setup, complete guides, and dual-repo architecture"
        ], cwd=repo_root)
        log_success("Local commit created successfully.")
    else:
        log_info("Working tree clean, nothing new to commit.")

def setup_and_push_private(git_bin, gh_bin, repo_root, username, repo_name):
    full_name = f"{username}/{repo_name}"
    log_info(f"Setting up Private Repository: {C_BOLD}{full_name}{C_RESET}")

    # Check if repo already exists on GitHub
    check = subprocess.run([gh_bin, "repo", "view", full_name], capture_output=True, text=True)
    if check.returncode != 0:
        log_info(f"Creating new private repository {full_name} on GitHub...")
        run_cmd([
            gh_bin, "repo", "create", repo_name,
            "--private",
            f"--description=inxernal - Core Internal Automation Suite, C++ Native Hook Engine & Reverse Engineering Harness (Private)"
        ], cwd=repo_root)
    else:
        log_info(f"Repository {full_name} already exists on GitHub.")

    remote_url = f"https://github.com/{full_name}.git"
    
    # Configure remote 'origin-private' or 'origin'
    remotes_res = run_cmd([git_bin, "remote"], cwd=repo_root)
    remotes = remotes_res.stdout.split()
    remote_name = "origin" if "origin" not in remotes else "origin-private"
    if remote_name in remotes:
        run_cmd([git_bin, "remote", "set-url", remote_name, remote_url], cwd=repo_root)
    else:
        run_cmd([git_bin, "remote", "add", remote_name, remote_url], cwd=repo_root)

    log_info(f"Pushing main branch to {remote_name} ({remote_url})...")
    run_cmd([git_bin, "push", "-u", remote_name, "main", "--force"], cwd=repo_root)
    log_success(f"Private repository published: https://github.com/{full_name}")
    return f"https://github.com/{full_name}"

def setup_and_push_public(git_bin, gh_bin, repo_root, username, repo_name):
    full_name = f"{username}/{repo_name}"
    log_info(f"Setting up Public Repository: {C_BOLD}{full_name}{C_RESET}")

    # Check if repo already exists on GitHub
    check = subprocess.run([gh_bin, "repo", "view", full_name], capture_output=True, text=True)
    if check.returncode != 0:
        log_info(f"Creating new public repository {full_name} on GitHub...")
        run_cmd([
            gh_bin, "repo", "create", repo_name,
            "--public",
            f"--description=🌾 #1 Free Hay Day Bot & Auto-Farming Tool for LDPlayer 9. Fully automatic wheat farming, harvesting, planting, roadside shop selling, Promon SHIELD bypass, and Quago anti-cheat blocker. Zero setup required!"
        ], cwd=repo_root)
    else:
        log_info(f"Repository {full_name} already exists on GitHub.")

    remote_url = f"https://github.com/{full_name}.git"

    # Configure remote 'origin-public'
    remotes_res = run_cmd([git_bin, "remote"], cwd=repo_root)
    remotes = remotes_res.stdout.split()
    remote_name = "origin-public"
    if remote_name in remotes:
        run_cmd([git_bin, "remote", "set-url", remote_name, remote_url], cwd=repo_root)
    else:
        run_cmd([git_bin, "remote", "add", remote_name, remote_url], cwd=repo_root)

    log_info(f"Pushing main branch to {remote_name} ({remote_url})...")
    run_cmd([git_bin, "push", "-u", remote_name, "main", "--force"], cwd=repo_root)
    
    # Add SEO topics
    log_info("Setting repository topics for search engine and GitHub discovery...")
    topics = [
        "hayday", "hayday-bot", "hay-day", "hay-day-bot", "supercell",
        "game-bot", "auto-farm", "ldplayer", "frida", "android-bot",
        "automation", "python", "bot", "reverse-engineering"
    ]
    topic_args = []
    for t in topics:
        topic_args.extend(["--add-topic", t])
    try:
        run_cmd([gh_bin, "repo", "edit", full_name] + topic_args, check=False)
    except Exception:
        pass

    log_success(f"Public repository published: https://github.com/{full_name}")
    return f"https://github.com/{full_name}"

def main():
    parser = argparse.ArgumentParser(description="Automated dual GitHub repository publisher for inxernal.")
    parser.add_argument("--token", help="GitHub Personal Access Token (optional)")
    parser.add_argument("--private-name", default="hayday-core-private", help="Private repo name (default: hayday-core-private)")
    parser.add_argument("--public-name", default="hayday-bot", help="Public repo name (default: hayday-bot)")
    args = parser.parse_args()


    repo_root = Path(__file__).resolve().parent

    print(f"\n{C_BOLD}{C_MAGENTA}======================================================{C_RESET}")
    print(f"{C_BOLD}{C_MAGENTA}  inxernal - Automated GitHub Dual-Repository Setup  {C_RESET}")
    print(f"{C_BOLD}{C_MAGENTA}======================================================{C_RESET}\n")

    git_bin = get_git_path()
    gh_bin = get_gh_path()
    log_success(f"Git located: {git_bin}")
    log_success(f"GitHub CLI located: {gh_bin}")

    check_auth(gh_bin, token=args.token)
    username = get_github_username(gh_bin)
    log_success(f"Logged in as GitHub user: {C_BOLD}{username}{C_RESET}\n")

    init_local_git(git_bin, repo_root, username)

    # 1. Publish Private Repository
    private_url = setup_and_push_private(git_bin, gh_bin, repo_root, username, args.private_name)

    # 2. Publish Public Repository
    public_url = setup_and_push_public(git_bin, gh_bin, repo_root, username, args.public_name)

    print(f"\n{C_BOLD}{C_GREEN}======================================================{C_RESET}")
    print(f"{C_BOLD}{C_GREEN}  All Repositories Successfully Published to GitHub!  {C_RESET}")
    print(f"{C_BOLD}{C_GREEN}======================================================{C_RESET}\n")
    print(f"  🔒 {C_BOLD}Private Repository:{C_RESET} {private_url}")
    print(f"     ➔ Architecture Guide:  {private_url}/blob/main/README_PRIVATE.md")
    print(f"     ➔ Full Source Code & Native Engine Included\n")
    print(f"  🌐 {C_BOLD}Public Repository:{C_RESET}  {public_url}")
    print(f"     ➔ Complete User Guide: {public_url}/blob/main/README.md")
    print(f"     ➔ Automated 1-Click Setup Included\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"Execution failed: {e}")
        sys.exit(1)
