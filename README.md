### Project Manager 
 
Этот проект представляет собой бэкенд для автодеплоя веб-проектов, написанных на Django с использованием Docker Compose, Nginx, MySQL.
 
#### Key Features: 
- **Automatic Deployment**: Configure and deploy projects with minimal setup. 
- **Environment Management**: Support for development, testing, and production environments. 
- **Configuration Setup**: Centralized management of settings for Linux environments.

## Установка

1. Клонируйте репозиторий с помощью команды ```sh git clone https://github.com/Gricana/project_manager.git```
2. Перейдите в подпапку 'app' с помощью команды ```sh cd project_manager/app```
3. Установите необходимые зависимости, используя ```sh pip install -r requirements.txt```
4. установите необходимые переменные окружения, перечисленные в конфигурационном файла API **app/config.py**
5. установите необходимые переменные окружения, перечисленные в конфигурационном файле пакета, предназначееного для выполнения развертывания веб-проектов на Django **app/deploy/settings.py**.
   !!!Предварительно настройте [Yandex Cloud](https://yandex.cloud/), подключите и настройте сервис [yandex KMS](https://yandex.cloud/ru/docs/kms/) для выполнения шифрования файлов, а также приобретите SSL-сертификат для работы развернутых сайтов по протоколу HTTP
6. ВЫполнить миграции из директории **app**
   ```sh flask db init```
   ```sh flask db migrate -m "your message"```
   ```sh flask db migrate -m "your message"```
   ```sh flask db upgrade```
7. В финале нужно запустить ТОЛЬКО стартовый скрипт API run.py
   
   - ```sh
   flask run
   ```
   - либо с указанием хоста и порта
   
   - ```sh
   flask run --host=127.0.0.1 --port=6699
   ```
