class BitbucketClient(BaseClient):
    def __init__(self, token):
        super().__init__('https://api.bitbucket.org/2.0', token)

    def fetch_user_repositories(self):
        return self.get("repositories")

    def fetch_repo_contributors(self, workspace, repo_slug):
        return self.get(f"repositories/{workspace}/{repo_slug}/commits")
