from deploy.settings import *
import base64
import os
import requests
import urllib.parse


class ConfigStorage:
    """
    A class for managing and working with encryption of confidential data using the Yandex Cloud KMS (Key Management Service) cloud service.

    Designed to create keys, encrypt and decrypt configuration files.
    """

    def __init__(self, user_id: int, project_name: str):
        """
        Initializing the ConfigStorage object.

        :param user_id: Identifier of the user for whom the key is created.
        :type user_id: int
        :param project_name: The name of the project for which encryption is performed.
        :type project_name: str
        """
        self.project_name = project_name
        self.user_id = user_id

    def create_key(self):
        """
        Creating a key in Yandex Cloud KMS if the key does not already exist for this user.

        :return: ID of the created key, or None if key creation failed.
        :rtype: str or None
        """
        key_id = self.get_key_id(self.user_id)
        if not key_id:
            payload = {
                "folderId": YC_FOLDER_ID,
                "name": self.project_name,
                "description": str(self.user_id),
                "defaultAlgorithm": YC_KMS_ALGORITHM,
                "rotationPeriod": YC_KMS_ROTATION_PERIOD,
                "deletionProtection": False
            }

            response = requests.post(YC_KMS_ENDPOINT['create'],
                                     json=payload,
                                     headers={"Authorization": f"Bearer {YC_IAM_TOKEN}"})

            if response.status_code == 200:
                key_id = response.json().get('id')
                return key_id
            else:
                print(f"Key creation failed with status code {response.status_code} - {response.text}")
        return None

    @staticmethod
    def get_key(user_id):
        """
        Obtaining a key from Yandex Cloud KMS by user ID.

        :param user_id: User ID for which you want to get the key.
        :type user_id: int
        :return: Information about the key, or None if the key is not found.
        :rtype: dict or None
        """
        response = requests.get(YC_KMS_ENDPOINT['list'],
                                params={"folderId": urllib.parse.quote(YC_FOLDER_ID)},
                                headers={"Authorization": f"Bearer {YC_IAM_TOKEN}"})

        if response.status_code == 200:
            data = response.json()
            keys = data.get('keys', [])

            matching_keys = filter(lambda key: key["description"] == str(user_id), keys)
            return next(matching_keys, None)
        else:
            print(f"Failed to retrieve keys with status code {response.status_code} - {response.text}")
        return None

    @staticmethod
    def get_key_id(user_id):
        """
        Obtaining key ID by user ID.

        :param user_id: User ID for which you want to get the key ID.
        :type user_id: int
        :return: Key ID or None if the key is not found.
        :rtype: str or None
        """
        key = ConfigStorage.get_key(user_id)
        return key["primaryVersion"]["keyId"] if key else None

    def encrypt(self, file_content):
        """
        Encrypts the file contents and saves the encrypted contents to disk.

        :param file_content: Contents of the file to be encrypted.
        :type file_content: bytes
        :return: Key ID or None in case of error.
        :rtype: str or None
        """
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        key = ConfigStorage.get_key(self.user_id)

        if key:
            payload = {
                "versionId": key["primaryVersion"]["id"],
                "plaintext": encoded_content
            }

            response = requests.post(YC_KMS_ENDPOINT['encrypt'].format(keyId=key['id']), json=payload,
                                     headers={"Authorization": f"Bearer {YC_IAM_TOKEN}"})

            if response.status_code == 200:
                encrypted_content = response.json().get('ciphertext')
                self.to_file(encrypted_content)
                return key["primaryVersion"]["keyId"]
            else:
                print(f"Encryption failed with status code {response.status_code} - {response.text}")
        return None

    def to_file(self, ciphertext):
        """
        Saving encrypted content to a file on disk.

        :param ciphertext: Encrypted content.
        :type ciphertext: str
        """
        target_dir = os.path.join(CONFIG_DIR, str(self.user_id))
        os.makedirs(target_dir, exist_ok=True)

        with open(os.path.join(target_dir, self.project_name), 'wb') as file:
            file.write(base64.b64decode(ciphertext))

    def decrypt(self):
        """
        Decrypts the contents of the file and returns the decrypted text.

        :return: The decrypted contents of the file, or None in case of error.
        :rtype: str or None
        """
        target_file = os.path.join(CONFIG_DIR, str(self.user_id), self.project_name)

        if os.path.exists(target_file):
            key = ConfigStorage.get_key(self.user_id)

            if key:
                with open(target_file, 'rb') as file:
                    encrypted_content = file.read()

                payload = {
                    "versionId": key["primaryVersion"]["id"],
                    "ciphertext": base64.b64encode(encrypted_content).decode('utf-8')
                }

                response = requests.post(YC_KMS_ENDPOINT['decrypt'].format(keyId=key['id']), json=payload,
                                         headers={"Authorization": f"Bearer {YC_IAM_TOKEN}"})

                if response.status_code == 200:
                    decrypted_content = base64.b64decode(response.json().get('plaintext')).decode('utf-8')
                    return decrypted_content
                else:
                    print(f"Decryption failed with status code {response.status_code} - {response.text}")
        return None
