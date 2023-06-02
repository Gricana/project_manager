from deploy.settings import PROJECT_DIR
from git import Repo
import os
import re
import shutil


class ProjectPreparerMeta(type):
    def __new__(cls, name, bases, attrs):
        if "__prepare_project__" not in attrs:
            raise NotImplementedError("Subclasses must implement __prepare_project__ method.")

        return super().__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.__prepare_project__()
        return instance


class ProjectRunner(metaclass=ProjectPreparerMeta):

    PROJECT_TEMPLATE = "{repo_name}_{user_id}"

    def __init__(self, repo_url, user_id):
        self.repo_url = repo_url
        self.user_id = str(user_id)
        self.project_name = None

    def __prepare_project__(self):
        self.generate_project_dir()
        self.clone_repository()
        self.check_dependencies()

    def generate_project_dir(self):
        repo_name = re.search(r"/([^/]+).git$", self.repo_url).group(1)
        self.project_name = self.PROJECT_TEMPLATE.format(repo_name, self.user_id)

    def clone_repository(self):
        repo_dir = os.path.join(PROJECT_DIR, self.project_name)
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        Repo.clone_from(self.repo_url, repo_dir)

    def check_dependencies(self):
        requirements_file = os.path.join(self.project_path, self.project_name, "requirements.txt")
        if not os.path.exists(requirements_file):
            raise FileNotFoundError("requirements.txt file not found.")

    def setup_containers(self):
        pass

    def setup_nginx(self):
        pass

    def setup_gunicorn(self):
        pass


class DjangoRunner(ProjectRunner):
    def __prepare_project__(self):
        super().__prepare_project__()


runner = ProjectRunner(repo_url="https://github.com/your/repository.git", user_id=32423525626)
runner.setup_containers()
runner.setup_nginx()
runner.setup_gunicorn()

