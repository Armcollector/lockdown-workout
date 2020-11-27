import os
import urllib.parse

basedir = os.path.abspath(os.path.dirname(__file__))


if "DB_CONNECTIONSTRING" in os.environ:
    params = urllib.parse.quote_plus(os.environ.get("DB_CONNECTIONSTRING"))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "iR33OXoRSUj5"
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect={}".format(params)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    VERSION = "2.1.0"
    WTF_CSR_ENABLED = True
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 50
    MAINTITLE = "BGs Lockdown Workout "
    INSTANCE = "BG"
    # MAINTITLE = "Sonats Lockdown Workout "
    # INSTANCE = "SONAT"
