import os

# Configuration and project dirs
CONFIG_DIR = os.getenv('CONFIG_DIR', '/path/to/config')  # Сonfiguration dir
PROJECT_DIR = os.getenv('PROJECT_DIR', '/path/to/project')  # Project dir

# Configuration template dir
TEMPLATE_CONF_DIR = os.getenv('TEMPLATE_CONF_DIR')

# Path to SSL certificates and keys
SSL_PATH = os.getenv('SSL_PATH')  # Common path to SSL files
SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')  # Path to the SSL certificate
SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')  # Path to the SSL key

# MySQL root user password
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')

# Yandex Cloud configuration
# Yandex Cloud folder ID
# https://yandex.cloud/ru/docs/resource-manager/operations/folder/create
YC_FOLDER_ID = os.getenv('YC_FOLDER_ID')
# IAM token Yandex Cloud
# https://yandex.cloud/ru/docs/iam/concepts/authorization/iam-token#lifetime
YC_IAM_TOKEN = os.getenv('YC_IAM_TOKEN')

# KMS configuration
# https://yandex.cloud/ru/docs/kms/
YC_KMS_ALGORITHM = 'AES_256'  # KMS algorithm
YC_KMS_ROTATION_PERIOD = '604800s'  # KMS key rotation period (in seconds)

# KMS API endpoints
YC_KMS_ENDPOINT = {
    'create': 'https://kms.api.cloud.yandex.net/kms/v1/keys/',  # Endpoint for generating keys
    'list': 'https://kms.api.cloud.yandex.net/kms/v1/keys/',  # Endpoint for getting a list of keys
    'encrypt': 'https://kms.yandex/kms/v1/keys/{keyId}:encrypt',  # Endpoint for data encryption
    'decrypt': 'https://kms.yandex/kms/v1/keys/{keyId}:decrypt',  # Endpoint for data decryption
}

# Necessary variables for starting and running a web project (for now only Django projects!)
REQUIRED_VARIABLES = {
    'SETTINGS': ['DJANGO_SETTINGS_MODULE', 'SECRET_KEY'],  # Переменные настройки Django
    'DB': ['DATABASE_NAME', 'DATABASE_USER', 'DATABASE_PASSWORD'],  # Переменные настройки базы данных
    'ADMIN': ['ADMIN_USERNAME', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']  # Переменные настройки администратора
}
