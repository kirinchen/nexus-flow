from github import Github

from nexus_flow.infra import config


class GitHubClientService:
    def __init__(self, token: str):
        self.client = Github(token)

    def upload_file(self, repo_name, file_path, file_content, commit_message, branch="main"):
        """
        上傳文件到 GitHub 儲存庫。

        :param repo_name: 儲存庫名稱，例如 'username/repository'
        :param file_path: 儲存庫中的文件路徑和檔名
        :param file_content: 文件的內容
        :param commit_message: 提交訊息
        :param branch: 目標分支，預設為 'main'
        :return: None
        """
        repo = self.client.get_repo(repo_name)
        # 檢查文件是否已存在
        try:
            contents = repo.get_contents(file_path, ref=branch)
            # 更新文件
            repo.update_file(contents.path, commit_message, file_content, contents.sha, branch=branch)
            print("File updated successfully!")
        except Exception as e:
            # 新增文件
            repo.create_file(file_path, commit_message, file_content, branch=branch)
            print("File created successfully!")

    def load_file(self, repo_name, file_path, branch="main"):
        """
        從 GitHub 儲存庫載入文件。

        :param repo_name: 儲存庫名稱，例如 'username/repository'
        :param file_path: 儲存庫中的文件路徑和檔名
        :param branch: 文件所在分支，預設為 'main'
        :return: 文件內容，如果載入失敗則回傳 None
        """
        repo = self.client.get_repo(repo_name)
        file_content = repo.get_contents(file_path, ref=branch)
        content = file_content.decoded_content.decode()
        print("File content loaded successfully!")
        return content


_instance: GitHubClientService = None


def get_instance():
    global _instance
    if _instance is None:
        github_token: str = config.env('GITHUB_TOKEN')
        _instance = GitHubClientService(token=github_token)
    return _instance
