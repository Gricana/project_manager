import os


class Config:
    """
    Class for storing API configuration parameters.
    """

    def __init__(self):
        self.DEBUG = False

        self.SECRET_KEY = os.environ.get('SECRET_KEY')

        # MySQL database connection parameters
        self.SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{username}:{password}@{hostname}/{dbname}'.format(
            username=os.environ.get('HOST_USER'),
            password=os.environ.get('HOST_PASSWORD'),
            hostname=os.environ.get('DB_HOST'),
            dbname=os.environ.get('DB_NAME')
        )

        self.SQLALCHEMY_TRACK_MODIFICATIONS = True

        # SSL options
        self.SSL_ENABLED = True
        self.SSL_CERTIFICATE = os.environ.get('SSL_CERT_PATH')
        self.SSL_PRIVATE_KEY = os.environ.get('SSL_KEY_PATH')

        # Security settings
        self.SERVER_NAME = 'ewdbot.com'
        self.PREFERRED_URL_SCHEME = 'https'
        self.SESSION_COOKIE_SECURE = True
        self.REMEMBER_COOKIE_SECURE = True
        self.FORCE_HTTPS = True
        self.SSL_REDIRECT_STATUS = 301
