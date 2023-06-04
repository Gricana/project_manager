from deploy.settings import PROJECT_DIR
from dotenv import dotenv_values
from git import Repo
from .exceptions import SecurityIssueError
import importlib
import io
import os
import re
import shutil
import subprocess


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

    def __init__(self, repo_url: str, subdomain: str, user_id: int):
        self.repo_url = repo_url
        self.subdomain = subdomain
        self.user_id = str(user_id)
        self.dir_name = None
        self.abs_path = None

    def __prepare_project__(self):
        self.generate_project_dir()
        self.clone_repository()
        self.check_dependencies()
        self.scan()

    def generate_project_dir(self):
        repo_name = re.search(r"/([^/]+).git$", self.repo_url).group(1)
        self.dir_name = self.PROJECT_TEMPLATE.format(repo_name=repo_name, user_id=self.user_id)

    def clone_repository(self):
        self.abs_path = os.path.join(PROJECT_DIR, self.dir_name)
        self.delete_project()
        Repo.clone_from(self.repo_url, self.abs_path)

    def delete_project(self):
        if os.path.exists(self.abs_path):
            shutil.rmtree(self.abs_path)

    def check_dependencies(self):
        requirements_file = os.path.join(self.abs_path, "requirements.txt")
        if not os.path.exists(requirements_file):
            raise FileNotFoundError("requirements.txt file not found.")

    def scan(self):
        files_to_scan = []

        for root, dirs, files in os.walk(self.abs_path):
            for file in files:
                file_path = os.path.join(root, file)
                files_to_scan.append(file_path)

        issues_found = False

        for file_path in files_to_scan:
            command = f"bandit -r {file_path}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                issues_found = True

            if issues_found:
                self.delete_project()
                raise SecurityIssueError(f"В проекте обнаружены ошибки безопасности \n{result.stdout}")

    @staticmethod
    def settings_to_dict(decrypted_settings: str):
        return dotenv_values(stream=io.StringIO(decrypted_settings))

    def setup_containers(self):
        pass

    def setup_nginx(self):
        pass

    def setup_gunicorn(self):
        pass


class DjangoRunner(ProjectRunner):

    def __init__(self, repo_url, subdomain, user_id):
        super().__init__(repo_url, subdomain, user_id)
        self.settings_module = None

    def __prepare_project__(self):
        super().__prepare_project__()
        self.check_settings_module()

    def check_settings_module(self, module: str):
        try:
            os.chdir(self.abs_path)
            self.settings_module = importlib.import_module(module)
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f'Модуль с настройками {module} не найден!')

    def get_settings(self, decrypted_settings: str):
        settings_dict = ProjectRunner.settings_to_dict(decrypted_settings)

        django_settings_module = settings_dict.get('DJANGO_SETTINGS_MODULE')
        self.check_settings_module(django_settings_module)

        required_settings = {
            'STATIC_URL': getattr(self.settings_module, 'STATIC_URL', '/static/'),
            'STATIC_ROOT': getattr(self.settings_module, 'STATIC_ROOT', self.abs_path + '/static/'),
            'MEDIA_URL': getattr(self.settings_module, 'MEDIA_URL', '/media/'),
            'MEDIA_ROOT': getattr(self.settings_module, 'MEDIA_ROOT', self.abs_path + '/media/'),
        }
        return required_settings

    def set_host(self):
        with open(self.settings_module.__file__, 'r') as file:
            content = file.read()

        content = re.sub(pattern=r'(ALLOWED_HOSTS\s*=\s*\[).*?(\])',
                         repl= rf'\1"{self.subdomain}.ewdbot.com"\2',
                         string=content, flags=re.DOTALL)

        with open(self.settings_module.__file__, 'w') as file:
            file.write(content)

