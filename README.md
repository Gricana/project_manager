### Project Manager

This project is a backend for autodeployment of web projects written in Django using Docker Compose, Nginx, MySQL.

#### 🌟 Key Features:

- **Automatic Deployment**: Configure and deploy projects with minimal setup.

- **Environment Management**: Support for development, testing, and production environments.

- **Configuration Setup**: Centralized management of settings for Linux environments.

## 🛠️ Installation

1. Clone the repository using the command
```sh
git clone https://github.com/Gricana/project_manager.git
```
2. Go to the 'app' subfolder using the command
```sh
cd project_manager/app
```
3. Install the necessary dependencies using
```sh
pip install -r requirements.txt
```
## Usage

1. set the necessary environment variables listed in the API configuration file **app/config.py**
2. set the necessary environment variables listed in the configuration file of the package intended for performing deployment of web projects on Django **app/deploy/settings.py**.
- 📢Pre-configure [Yandex Cloud](https://yandex.cloud/), connect and configure the [Yandex KMS](https://yandex.cloud/ru/docs/kms/) service to encrypt files, and purchase an SSL certificate for deployed sites to work over HTTP

3. Perform migrations from the **app** directory
```sh
flask db init
```

```sh
flask db migrate -m "your message"
```

```sh
flask db upgrade
```

4. Finally, you need to run ONLY the API start script run.py
```sh
flask run
```
- or specifying the host and port

```sh
flask run --host=127.0.0.1 --port=6699
```
## Contributing
  Contributions are welcome! If you have suggestions for improvements or find any bugs, please open an issue or submit a pull request on GitHub.
