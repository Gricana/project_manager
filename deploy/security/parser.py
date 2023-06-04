from abc import ABC, abstractmethod
from deploy.settings import REQUIRED_VARIABLES
import json


class Config(ABC):

    extensions = {}

    def __init__(self):
        self._config = {}

    @abstractmethod
    def _load(self):
        pass

    def check_required(self):
        if not all(v in self._config.get(section, {}) for section, vars in REQUIRED_VARIABLES.items() for v in vars):
            raise KeyError('Указан неполный список обязательных переменных')

    def _to_env_format(self):
        var_list = [f"{key.upper()}={value}" for key, value in self._config.items()]
        return "\n".join(var_list)

    def convert(self):
        self._load()
        self.check_required()
        return self._to_env_format()

    @classmethod
    def register(cls, extension):
        def create(subclass):
            cls.extensions[extension] = subclass
            return subclass
        return create

    @classmethod
    def from_content(cls, content, extension):
        for ext, subclass in cls.extensions.items():
            if extension.lower() == ext.lower():
                return subclass(content)
        raise ValueError('Unsupported file format')


@Config.register(extension='json')
class JSONConfig(Config):
    
    def __init__(self, content):
        super().__init__()
        self.__content = content

    def _load(self):
        try:
            self._config = json.loads(self.__content)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError('Неправильный формат указания переменных в JSON-е', e.doc, e.pos)


@Config.register(extension='txt')
class TxtConfig(Config):

    def __init__(self, content):
        super().__init__()
        self.__content = content

    def _load(self):
        try:
            lines = self.__content.split('\n')
            self._config = {key.strip(): value.strip() for line in lines if line.strip() for key, value in [line.split('=')]}
        except ValueError:
            raise ValueError('Неправильный формат указания переменных в текстовом файле')
