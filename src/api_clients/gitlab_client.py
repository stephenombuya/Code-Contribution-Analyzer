class GitLabClient(BaseClient):
    def __init__(self, token):
        super().__init__('https://gitlab.com/api/v4', token)

    def fetch_user_projects(self):
        return self.get("projects")

    def fetch_project_contributors(self, project_id):
        return self.get(f"projects/{project_id}/repository/contributors")
