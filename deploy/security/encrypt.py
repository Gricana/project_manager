from deploy.settings import *
import json
import os
import requests
import urllib.parse


class ConfigStorage:
    def __init__(self, user_id: int, project_name: str):
        self.project_name = project_name
        self.user_id = user_id

    def create_key(self):
        if not ConfigStorage.get_key(self.user_id):
            payload = {
                "folderId": YC_FOLDER_ID,
                "name": str(self.user_id),
                "description": self.project_name,
                "defaultAlgorithm": YC_KMS_ALGORITHM,
                "rotationPeriod": YC_KMS_ROTATION_PERIOD,
                "deletionProtection": False
            }

            response = requests.post(YC_KMS_ENDPOINT['create'], json=payload,
                                     headers={
                                         "Authorization": "Bearer {}".format(YC_IAM_TOKEN),
                                     })

            if response.status_code == 200:
                key_id = response.json()['id']
                return key_id
            else:
                print(f"Key creation failed with status code {response.status_code} - {response.text}")
                return None

    @staticmethod
    def get_key(user_id):
        response = requests.get(YC_KMS_ENDPOINT['list'],
                                params={"folderId": urllib.parse.quote(YC_FOLDER_ID)},
                                headers={
                                    "Authorization": "Bearer {}".format(YC_IAM_TOKEN)
                                })
        print(response.status_code)
        if response.status_code == 200:
            data = response.json()
            keys = data['keys']

            matching_keys = filter(lambda key: key["name"] == str(user_id), keys)
            matching_key = next(matching_keys, None)
            print(keys)
            if matching_key:
                return matching_key
        else:
            print(f"Failed to retrieve keys with status code {response.status_code} - {response.text}")
        return None

    @staticmethod
    def get_key_id(user_id):
        key = ConfigStorage.get_key(user_id)
        return key["primaryVersion"]["keyId"] if key else None

    def encrypt(self, file_content):
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        key = ConfigStorage.get_key(self.user_id)

        payload = {
            "versionId": key["primaryVersion"]["id"],
            "plaintext": encoded_content
        }

        response = requests.post(YC_KMS_ENDPOINT['encrypt'].format(keyId=key['id']), json=payload,
                                 headers={
                                     "Authorization": "Bearer {}".format(YC_IAM_TOKEN),
                                 })

        if response.status_code == 200:
            encrypted_content = response.json()['ciphertext']
            self.to_file(encrypted_content)
        else:
            print(f"Encryption failed with status code {response.status_code} - {response.text}")
            return None

    def to_file(self, ciphertext):
        target_dir = os.path.join(CONFIG_DIR, str(self.user_id))
        os.makedirs(target_dir, exist_ok=True)

        with open(os.path.join(target_dir, self.project_name), 'wb') as file:
            file.write(base64.b64decode(ciphertext))

    def decrypt(self):
        target_file = os.path.join(CONFIG_DIR, str(self.user_id), self.project_name)

        if os.path.exists(target_file):
            key = ConfigStorage.get_key(self.user_id)

            with open(target_file, 'rb') as file:
                encrypted_content = file.read()

            payload = {
                "versionId": key["primaryVersion"]["id"],
                "ciphertext": base64.b64encode(encrypted_content).decode('utf-8')
            }

            response = requests.post(YC_KMS_ENDPOINT['decrypt'].format(keyId=key['id']), json=payload,
                                     headers={
                                         "Authorization": "Bearer {}".format(YC_IAM_TOKEN),
                                     })

            if response.status_code == 200:
                decrypted_content = base64.b64decode(response.json()['plaintext']).decode('utf-8')
                return decrypted_content
            else:
                print(f"Decryption failed with status code {response.status_code} - {response.text}")
        return None
