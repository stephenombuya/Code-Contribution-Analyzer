class GitHubClient(BaseClient):
    def __init__(self, token):
        super().__init__('https://api.github.com', token)

    def fetch_user_repos(self, username):
        return self.get(f"users/{username}/repos")

    def fetch_repo_contributors(self, owner, repo):
        return self.get(f"repos/{owner}/{repo}/contributors")
