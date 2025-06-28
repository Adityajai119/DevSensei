import requests
from github import Github
from app.config import config
from typing import List, Dict, Any, Optional
import base64

class GitHubService:
    def __init__(self):
        self.github = Github(config.GITHUB_TOKEN)
        self.is_available = True

    async def search_repositories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            repos = self.github.search_repositories(query=query, sort="stars", order="desc")
            results = []
            for repo in repos[:limit]:
                results.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "url": repo.html_url,
                    "default_branch": repo.default_branch,
                    "topics": list(repo.get_topics()) if repo.get_topics() else []
                })
            return results
        except Exception as e:
            print(f"Error in GitHub repository search: {e}")
            return []

    async def get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        try:
            user = self.github.get_user(username)
            repos = user.get_repos()
            results = []
            for repo in repos:
                results.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "url": repo.html_url,
                    "default_branch": repo.default_branch,
                    "topics": list(repo.get_topics()) if repo.get_topics() else []
                })
            return results
        except Exception as e:
            print(f"Error in GitHub user repositories: {e}")
            return []

    async def get_repository_info(self, owner: str, repo_name: str) -> Dict[str, Any]:
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "url": repo.html_url,
                "default_branch": repo.default_branch,
                "topics": list(repo.get_topics()) if repo.get_topics() else [],
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "size": repo.size,
                "open_issues": repo.open_issues_count,
                "license": repo.license.name if repo.license else None,
                "readme": await self._get_readme_content(repo)
            }
        except Exception as e:
            print(f"Error in GitHub repository info: {e}")
            return {}

    async def get_repository_files(self, owner: str, repo_name: str, path: str = "") -> List[Dict[str, Any]]:
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            contents = repo.get_contents(path)
            results = []
            for content in contents:
                file_info = {
                    "name": content.name,
                    "path": content.path,
                    "type": content.type,
                    "size": content.size,
                    "url": content.html_url,
                    "download_url": content.download_url
                }
                if content.type == "file" and content.size < 1024 * 1024:
                    try:
                        file_content = content.decoded_content.decode('utf-8')
                        file_info["content"] = file_content
                        file_info["language"] = self._detect_language(content.name)
                    except:
                        file_info["content"] = None
                        file_info["language"] = None
                results.append(file_info)
            return results
        except Exception as e:
            print(f"Error in GitHub repository files: {e}")
            return []

    async def get_repository_structure(self, owner: str, repo_name: str) -> Dict[str, Any]:
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            def get_directory_structure(path=""):
                try:
                    contents = repo.get_contents(path)
                    structure = {}
                    for content in contents:
                        if content.type == "dir":
                            structure[content.name] = {
                                "type": "directory",
                                "path": content.path,
                                "children": get_directory_structure(content.path)
                            }
                        else:
                            structure[content.name] = {
                                "type": "file",
                                "path": content.path,
                                "size": content.size,
                                "language": self._detect_language(content.name)
                            }
                    return structure
                except:
                    return {}
            return {
                "repo_name": repo_name,
                "owner": owner,
                "structure": get_directory_structure()
            }
        except Exception as e:
            print(f"Error in GitHub repository structure: {e}")
            return {}

    async def _get_readme_content(self, repo) -> Optional[str]:
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')
        except:
            return None

    def _detect_language(self, filename: str) -> Optional[str]:
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.html': 'html',
            '.css': 'css',
            '.md': 'markdown',
            '.json': 'json',
            '.xml': 'xml',
            '.yml': 'yaml',
            '.yaml': 'yaml'
        }
        for ext, lang in extensions.items():
            if filename.endswith(ext):
                return lang
        return None

github_service = GitHubService() 