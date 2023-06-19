import os

CONFIG_DIR = os.getenv('CONFIG_DIR', '/path/to/config')
PROJECT_DIR = os.getenv('PROJECT_DIR', '/path/to/project')
TEMPLATE_CONF_DIR = os.getenv('TEMPLATE_CONF_DIR')
SSL_PATH = os.getenv('SSL_PATH')
SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')
SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')

YC_FOLDER_ID = os.getenv('YC_FOLDER_ID')
YC_IAM_TOKEN = os.getenv('YC_IAM_TOKEN')
YC_KMS_ALGORITHM = 'AES_256'
YC_KMS_ROTATION_PERIOD = '604800s'


YC_KMS_ENDPOINT = {
    'create': 'https://kms.api.cloud.yandex.net/kms/v1/keys/',
    'list': 'https://kms.api.cloud.yandex.net/kms/v1/keys/',
    'encrypt': 'https://kms.yandex/kms/v1/keys/{keyId}:encrypt',
    'decrypt': 'https://kms.yandex/kms/v1/keys/{keyId}:decrypt',
}

REQUIRED_VARIABLES = {
    'SETTINGS': ['DJANGO_SETTINGS_MODULE', 'SECRET_KEY'],
    'DB': ['DATABASE_NAME', 'DATABASE_USER', 'DATABASE_PASSWORD'],
    'ADMIN': ['ADMIN_USERNAME', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
}

