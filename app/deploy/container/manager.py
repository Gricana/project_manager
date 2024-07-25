from .prepare import DjangoPrepare
from deploy.security.parser import Config
from deploy.security.encrypt import ConfigStorage


class DjangoManager:
    """
    Manager for managing the deployment of Django projects

    This class provides methods for starting, restarting and stopping projects
    """

    def __init__(self, **kwargs):
        """
        Initialize DjangoManager with the project's staging object

        :param kwargs: Parameters for creating a DjangoPrepare object
        """
        self.prepare = DjangoPrepare(**kwargs)

    @classmethod
    def start(cls, **kwargs):
        """
        Starting a new Django project

        1. Creates and encrypts the project configuration
        2. Builds a Docker container
        3. Launches project services

        :param kwargs: Options for project deployment, including 'config', 'ext', 'id', 'name', and 'repo_url'.
        :return: True if the project was launched successfully, otherwise False.
        """
        # Create and encrypt project configuration
        config = Config.from_content(content=kwargs['config'], extension=kwargs['ext'])
        vars = config.convert()
        conf_storage = ConfigStorage(user_id=kwargs['id'], project_name=kwargs['name'])
        conf_storage.create_key()
        conf_storage.encrypt(vars)

        # Initialize DjangoManager and start deployment
        cls.manager = cls(repo_url=kwargs['repo_url'], id=kwargs['id'],
                          subdomain=kwargs['name'], decrypted_settings=conf_storage.decrypt())
        build_status = cls.manager.prepare.build_container()
        up_status = cls.manager.prepare.up_services()

        # Check deployment success
        return not (build_status or up_status)

    @classmethod
    def restart(cls, **kwargs):
        """
        Restarting the current Django project

        Stops the current project and then starts it again

        :param kwargs: Parameters for project deployment
        :return: The result of calling the start method
        """
        cls.stop(**kwargs)
        return cls.start(**kwargs)

    @classmethod
    def stop(cls, **kwargs):
        """
        Stopping the current Django project

        1. Stops and deletes Docker containers and images
        2. Deletes the project

        :param kwargs: Parameters for identifying the project
        """
        if cls.manager:
            cls.manager.prepare.down_services()
            cls.manager.prepare.delete_image()
            cls.manager.prepare.delete()
            cls.manager.prepare = None
