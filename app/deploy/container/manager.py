from .prepare import DjangoPrepare
from deploy.security.parser import Config
from deploy.security.encrypt import ConfigStorage


class DjangoManager:

    def __init__(self, **kwargs):
        self.prepare = DjangoPrepare(**kwargs)

    @classmethod
    def start(cls, **kwargs):
        config = Config.from_content(content=kwargs['config'], extension=kwargs['ext'])
        vars = config.convert()
        conf_storage = ConfigStorage(user_id=kwargs['id'], project_name=kwargs['name'])
        conf_storage.create_key()
        conf_storage.encrypt(vars)

        cls.manager = cls(repo_url=kwargs['repo_url'], id=kwargs['id'],
                          subdomain=kwargs['name'], decrypted_settings=conf_storage.decrypt())
        build_status = manager.prepare.build_container()
        up_status = manager.prepare.up_services()

        if any([build_status, up_status]):
            return False
        return True

    @classmethod
    def restart(cls, **kwargs):
        DjangoManager.stop()
        return DjangoManager.start(**kwargs)

    @classmethod
    def stop(cls, **kwargs):
        cls.manager.prepare.down_services()
        cls.manager.prepare.delete_image()
        cls.manager.prepare.delete()
        cls.manager.prepare = None
