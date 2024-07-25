from app.deploy.settings import PROJECT_DIR, SSL_PATH, TEMPLATE_CONF_DIR, SSL_CERT_PATH, SSL_KEY_PATH
from dotenv import dotenv_values
from git import Repo
from app.deploy.container.exceptions import SecurityIssueError
import importlib
import io
import os
import re
import stat
import subprocess
import yaml


class ProjectPreparerMeta(type):
    """
    Metaclass for checking the presence of the __prepare_project__ method in subclasses.
    """
    def __new__(cls, name, bases, attrs):
        if "__prepare_project__" not in attrs:
            raise NotImplementedError("Subclasses must implement __prepare_project__ method.")
        return super().__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.__prepare_project__()
        return instance


class ProjectPrepare(metaclass=ProjectPreparerMeta):
    """
    A class for preparing a project for deployment
    """
    PROJECT_TEMPLATE = "{repo_name}_{user_id}"

    def __init__(self, repo_url: str, subdomain: str, user_id: int, decrypted_settings: str):
        self.repo_url = repo_url  # URL repository
        self.subdomain = subdomain  # The project subdomain
        self.user_id = str(user_id)  # User ID
        self.__decrypted_settings = decrypted_settings  # Decrypted settings

        self.dir_name = None  # Project dir name
        self.abs_path = None  # Absolute path to the project

    def __prepare_project__(self):
        """
        The main method for preparing a project
        """
        self.generate_project_dir()
        self.clone()
        self.check_dependencies()
        self.scan()

    def generate_project_dir(self):
        """
        Generating the name of the project dir
        """
        repo_name = re.search(r"/([^/]+).git$", self.repo_url).group(1)
        self.dir_name = self.PROJECT_TEMPLATE.format(repo_name=repo_name, user_id=self.user_id)

    def clone(self):
        """
        Cloning a git repository
        """
        self.abs_path = os.path.join(PROJECT_DIR, self.dir_name)
        self.delete()
        Repo.clone_from(self.repo_url, self.abs_path)

    def delete(self):
        """
        Deleting an existing project dir
        """
        if os.path.exists(self.abs_path):
            command = ["sudo", "rm", "-rf", self.abs_path]
            subprocess.run(command)

    # @staticmethod
    # def onerror(func, path, exc_info):
    #     """
    #     Error handling when deleting files
    #     """
    #     os.chmod(path, stat.S_IWRITE)
    #     func(path)

    def check_dependencies(self):
        """
        Checking for a dependency file
        """
        requirements_file = os.path.join(self.abs_path, "requirements.txt")
        if not os.path.exists(requirements_file):
            raise FileNotFoundError("requirements.txt file not found.")

    def scan(self):
        """
        Scanning a project for vulnerabilities
        """
        files_to_scan = []

        for root, dirs, files in os.walk(self.abs_path):
            for file in files:
                file_path = os.path.join(root, file)
                files_to_scan.append(file_path)

        issues_found = False

        for file_path in files_to_scan:
            command = f"bandit -r {file_path} --severity-level medium --confidence-level high"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                issues_found = True

            if issues_found:
                self.delete()
                raise SecurityIssueError(f"В проекте обнаружены ошибки безопасности \n{result.stdout}")

    def settings_to_dict(self):
        """
        Convert decrypted settings into a dict
        """
        return dotenv_values(stream=io.StringIO(self.__decrypted_settings))

    def get_app_ports(self):
        """
        Obtaining free ports for an app.
        """
        port_scripts = [
            'get_free_app_port.sh',
            'get_free_nginx_port.sh',
            'get_free_redis_port.sh'
        ]

        port_keys = ['APP_PORT', 'NGINX_PORT', 'REDIS_PORT']
        ports = {}

        for script, key in zip(port_scripts, port_keys):
            try:
                result = subprocess.check_output(['bash', '-c', f'source {TEMPLATE_CONF_DIR}{script} && echo $PORT'])
                ports[key] = result.decode('utf-8').strip()
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to get port from {script}: {e.output}")

        return ports


class DjangoPrepare(ProjectPrepare):
    """
    A class for preparing a Django project for deployment.
    """

    def __init__(self, repo_url, subdomain, user_id, decrypted_settings):
        super().__init__(repo_url, subdomain, user_id, decrypted_settings)
        self.settings_module = ''
        self.__settings_dict = None

    def __prepare_project__(self):
        """
        Basic method for preparing a Django project
        """
        super().__prepare_project__()
        self.setup()

    def setup(self):
        """
        Project setup
        """
        self.extend_settings()
        self.setup_dockerfile()
        self.setup_sql()
        self.setup_reverse_nginx()
        self.setup_compose()
        self.set_host()

    def __check_settings_module(self, module: str):
        """
        Checking the presence of the settings module
        """
        try:
            prev_dir = os.getcwd()
            os.chdir(self.abs_path)
            self.settings_module = importlib.import_module(module)
            os.chdir(prev_dir)
        except ModuleNotFoundError:
            raise ModuleNotFoundError(f'Модуль с настройками {module} не найден!')

    def extend_settings(self):
        """
        Expanding project settings
        """
        self.__settings_dict = self.settings_to_dict()

        django_settings_module = self.__settings_dict.get('DJANGO_SETTINGS_MODULE')
        self.__check_settings_module(django_settings_module)

        required_settings = {
            'MYSQL_ROOT_PASSWORD': self.__settings_dict['DATABASE_PASSWORD'],
            'SETTINGS_MODULE': django_settings_module.split('.')[0],
            'SUBDOMAIN': f'{self.subdomain}',
            'DIR_NAME': self.dir_name,
            'SSL_PATH': SSL_PATH,
            'SSL_CERT_PATH': SSL_CERT_PATH,
            'SSL_KEY_PATH': SSL_KEY_PATH,
            'STATIC_URL': getattr(self.settings_module, 'STATIC_URL', '/static/'),
            'STATIC_ROOT': os.path.basename(getattr(self.settings_module, 'STATIC_ROOT', self.abs_path + '/static/')),
            'MEDIA_URL': getattr(self.settings_module, 'MEDIA_URL', '/media/'),
            'MEDIA_ROOT': os.path.basename(getattr(self.settings_module, 'MEDIA_ROOT', self.abs_path + '/media/')),
        }
        self.__settings_dict.update(required_settings)
        self.__settings_dict.update(self.get_app_ports())

    def set_host(self):
        """
        Setting the host in Django settings
        """
        with open(self.settings_module.__file__, 'r') as f:
            content = f.read()

        content = re.sub(pattern=r'(ALLOWED_HOSTS\s*=\s*\[).*?(\])',
                         repl=rf'\1"{self.subdomain}.ewdbot.com"\2',
                         string=content, flags=re.DOTALL)
        content = re.sub(pattern=r'(CSRF_TRUSTED_ORIGINS\s*=\s*\[).*?(\])',
                         repl=rf'\1"https://{self.subdomain}.ewdbot.com"\2',
                         string=content, flags=re.DOTALL)

        with open(self.settings_module.__file__, 'w') as file:
            file.write(content)

    def update_env(self):
        """
        Update environment variables
        """
        env_args = " ".join([f"{key}={value}" for key, value in self.__settings_dict.items()])
        build_args = " ".join([f"--build-arg {key}={value}" for key, value in self.__settings_dict.items()])
        return env_args, build_args

    def setup_compose(self):
        """
        Setting up docker-compose.yml file
        """
        with open(f'{TEMPLATE_CONF_DIR}docker-compose.yml', 'r') as file:
            compose_data = yaml.safe_load(file)
        compose_data['services']['web']['build']['args'].extend([f"{key}=${{{key}}}" for key in self.__settings_dict])
        compose_data['services']['web']['environment'].update({key: f"${{{key}}}" for key in self.__settings_dict})
        compose_data['services']['web']['volumes'] = [f'.:/{self.dir_name}']

        with open(os.path.join(self.abs_path, 'docker-compose.yml'), 'w') as file:
            yaml.dump(compose_data, file, indent=2)

    def setup_dockerfile(self):
        """
        Dockerfile setup
        """
        with open(f"{TEMPLATE_CONF_DIR}Dockerfile") as file:
            content = file.read()

        with open(os.path.join(self.abs_path, 'Dockerfile'), 'w') as file:
            file.write(content.format(DIR_NAME=self.__settings_dict['DIR_NAME']))

    def setup_sql(self):
        """
        Setting up the init.sql file
        """
        with open(f"{TEMPLATE_CONF_DIR}init.sql") as file:
            content = file.read()

        with open(os.path.join(self.abs_path, 'init.sql'), 'w') as file:
            file.write(content.format(**self.__settings_dict))

    def setup_nginx_container(self):
        """
        Setting up configuration for Nginx container
        """
        with open(f"{TEMPLATE_CONF_DIR}nginx.conf") as file:
            content = file.read()

        config_dir = os.path.join(self.abs_path, 'config')
        os.makedirs(config_dir, exist_ok=True)

        with open(os.path.join(config_dir, 'nginx.conf'), 'w') as file:
            file.write(content.format(**self.__settings_dict))

    def setup_reverse_nginx(self):
        """
        Setting up a reverse proxy for Nginx
        """
        with open(f"{TEMPLATE_CONF_DIR}reverse_nginx") as file:
            content = file.read()

        with open('/etc/nginx/sites-available/default', 'a') as file:
            file.write(content.format(**self.__settings_dict))

    def build_container(self):
        """
        Building a Docker container
        """
        env_args, build_args = self.update_env()
        command = env_args + ' docker compose build ' + build_args + ' --no-cache'
        subprocess.run(command, cwd=self.abs_path, shell=True)

    def up_services(self):
        """
        Running Docker services
        """
        env_args, _ = self.update_env()
        command = env_args + ' docker compose up -d'
        subprocess.run(command, cwd=self.abs_path, shell=True)
        subprocess.run(['sudo', 'service', 'nginx', 'restart'])

    def down_services(self):
        """
        Stopping Docker services
        """
        env_args, _ = self.update_env()
        subprocess.run(env_args + ' docker compose down', cwd=self.abs_path, shell=True)
