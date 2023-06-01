from abc import ABC, abstractmethod
import json


class Config(ABC):

    def __init__(self):
        self._config = {}

    @abstractmethod
    def _load(self):
        pass

    def _to_env_format(self):
        var_list = [f"{key.upper()}={value}" for key, value in self._config.items()]
        return "\n".join(var_list)

    def apply(self):
        self._load()
        return self._to_env_format()


class JSONConfig(Config):
    
    def __init__(self, content):
        super().__init__()
        self.__content = content

    def _load(self):
        try:
            self._config = json.loads(self.__content)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError('Неправильный формат указания переменных в JSON-е', e.doc, e.pos)


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
