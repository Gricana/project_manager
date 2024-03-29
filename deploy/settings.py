import os

CONFIG_DIR = os.getenv('CONFIG_DIR', '/path/to/config')
PROJECT_DIR = os.getenv('PROJECT_DIR', '/path/to/project')

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

