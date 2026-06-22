# pyrefly: ignore [missing-import]
import git
import os
import tempfile

def clone_repository(repo_url):
    # Create a completely fresh, isolated temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Clone the repository into this temporary directory
    git.Repo.clone_from(
        repo_url,
        temp_dir
    )

    return temp_dir