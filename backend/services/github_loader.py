# pyrefly: ignore [missing-import]
import git
import os
import tempfile
import re

def clone_repository(repo_url):
    # Validate and clean the GitHub URL
    if not repo_url:
        raise ValueError("Repository URL cannot be empty")
    
    # Ensure URL ends with .git for git clone
    if not repo_url.endswith('.git'):
        repo_url = repo_url + '.git'
    
    # Create a temporary directory with a shorter, Windows-compatible path
    # Use a fixed base temp directory to avoid long path issues on Windows
    base_temp = os.path.join(os.getcwd(), "temp_repos")
    os.makedirs(base_temp, exist_ok=True)
    
    # Generate a unique folder name using timestamp
    import time
    timestamp = str(int(time.time()))
    temp_dir = os.path.join(base_temp, f"repo_{timestamp}")
    
    # Ensure the directory doesn't exist
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Clone the repository into this temporary directory
        git.Repo.clone_from(
            repo_url,
            temp_dir
        )
        return temp_dir
    except git.exc.GitCommandError as e:
        # Clean up on failure
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError(f"Failed to clone repository: {str(e)}")