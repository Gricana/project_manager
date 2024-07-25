from abc import ABC, abstractmethod
from deploy.settings import REQUIRED_VARIABLES
import json


class Config(ABC):
    """
    Abstract base class for configurations

    This class provides common methods for loading configuration, checking required variables
    and converting the configuration into environment variable format.

    Supports extensions for various configuration formats.
    """

    extensions = {}

    def __init__(self):
        """
        Initialize an empty configuration dictionary
        """
        self._config = {}

    @abstractmethod
    def _load(self):
        """
        Abstract method for loading configuration.
        Must be implemented in subclasses.
        """
        pass

    def check_required(self):
        """
        Checking that all required variables are present in the configuration.

        :raises KeyError: If not all required variables are specified.
        """
        missing_vars = [
            (section, var) for section, vars in REQUIRED_VARIABLES.items()
            for var in vars if var not in self._config.get(section, {})
        ]
        if missing_vars:
            raise KeyError('Указан неполный список обязательных переменных')

    def _to_env_format(self):
        """
        Converting configuration to environment variable format.

        :return: Configuration as a line, where each line represents an environment variable.
        :rtype:str
        """
        var_list = [f"{key.upper()}={value}" for key, value in self._config.items()]
        return "\n".join(var_list)

    def convert(self):
        """
        Loading configuration, checking required variables and converting to environment variable format.

        :return: Configuration as a string of environment variables.
        :rtype:str
        """
        self._load()
        self.check_required()
        return self._to_env_format()

    @classmethod
    def register(cls, extension):
        """
        A decorator for registering configuration subclasses with support for various formats.

        :param extension: Configuration file extension.
        :type extension: str
        :return: Decorated configuration class.
        :rtype: type
        """

        def create(subclass):
            cls.extensions[extension] = subclass
            return subclass

        return create

    @classmethod
    def from_content(cls, content, extension):
        """
        Instantiating a configuration from a content string and an extension.

        :param content: Contents of the configuration file.
        :type content: str
        :param extension: Extension of the configuration file.
        :type extension: str
        :return: An instance of the configuration subclass.
        :rtype: Config
        :raises ValueError: If the extension format is not supported.
        """
        for ext, subclass in cls.extensions.items():
            if extension.lower() == ext.lower():
                return subclass(content)
        raise ValueError('Unsupported file format')


@Config.register(extension='json')
class JSONConfig(Config):
    """
    Конфигурация для формата JSON.

    Поддерживает загрузку конфигурации из строки в формате JSON.
    """

    def __init__(self, content):
        """
        Инициализация JSONConfig с содержимым JSON.

        :param content: Содержимое JSON-конфигурационного файла.
        :type content: str
        """
        super().__init__()
        self.__content = content

    def _load(self):
        """
        Загрузка конфигурации из JSON-строки.

        :raises json.JSONDecodeError: Если содержимое не является корректным JSON.
        """
        try:
            self._config = json.loads(self.__content)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError('Неправильный формат указания переменных в JSON-е', e.doc, e.pos)


@Config.register(extension='txt')
class TxtConfig(Config):
    """
    Конфигурация для формата текстового файла.

    Поддерживает загрузку конфигурации из строки в формате текстового файла с разделением на строки вида 'key=value'.
    """

    def __init__(self, content):
        """
        Инициализация TxtConfig с содержимым текстового файла.

        :param content: Содержимое текстового конфигурационного файла.
        :type content: str
        """
        super().__init__()
        self.__content = content

    def _load(self):
        """
        Загрузка конфигурации из строки текстового файла.

        :raises ValueError: Если содержимое не соответствует формату 'key=value'.
        """
        try:
            lines = self.__content.split('\n')
            self._config = {key.strip(): value.strip() for line in lines if line.strip() for key, value in
                            [line.split('=')]}
        except ValueError:
            raise ValueError('Неправильный формат указания переменных в текстовом файле')
