import os

from nexus_flow import nexus_flow_app
from nexus_flow.github import github_client_service

if __name__ == '__main__':
    wd_path = os.path.dirname(__file__)
    nexus_flow_app.initialize(wd_path)
    g_service = github_client_service.get_instance()
    readme_content = g_service.load_file(
        repo_name='domiearth/dsa-vecor-embed-doc-json',
        file_path='/README.md',
    )
    print(readme_content)
