import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'WR#&f&+%78er0we=%799eww+#7^90-;s'

    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'data', 'uploads')
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app', 'data', 'finance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Not setting this results in a performance warning

    # # Configure session to use filesystem (instead of signed cookies)
    # SESSION_PERMANENT = False
    # SESSION_TYPE = "filesystem"