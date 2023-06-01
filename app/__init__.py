import os


class Config:

    def __init__(self):
        self.DEBUG = False
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        self.SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{username}:{password}@{hostname}/{dbname}'.format(
            username=os.environ.get('HOST_USER'),
            password=os.environ.get('HOST_PASSWORD'),
            hostname=os.environ.get('DB_HOST'),
            dbname=os.environ.get('DB_NAME')
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = True
