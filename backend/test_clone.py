from services.github_loader import clone_repository

repo_url = input(
    "Enter GitHub Repository URL: "
)

repo_path = clone_repository(
    repo_url
)

print(
    f"Repository saved at: {repo_path}"
)