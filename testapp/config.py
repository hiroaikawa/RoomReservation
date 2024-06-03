DEBUG = True

DB_USER = '{db user}'
DB_PASS = '{db password}'
DB_HOST = '{db host}'
DB_NAME = '{db name}'
DB_PORT = {db port}
db_uri = "mysql+pymysql://{0}:{1}@{2}/{3}?charset=utf8".format(DB_USER, DB_PASS, DB_HOST, DB_NAME)
SQLALCHEMY_DATABASE_URI = db_uri

SQLALCHEMY_TRACK_MODIFICATIONS = False

LOGFILE_NAME = "DEBUG.log"