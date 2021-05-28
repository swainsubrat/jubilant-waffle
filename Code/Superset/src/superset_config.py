# pylint: disable=too-few-public-methods,wildcard-import,undefined-variable
"""
Contains Superset configs
"""
import os

from superset.config import *  # NOSONAR
from werkzeug.contrib.cache import RedisCache  # pylint: disable=no-name-in-module

# from superset.config import * is required for Superset to function normally


def get_env_variable(var_name, default=None):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError as ex:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg) from ex


invocation_type = get_env_variable("INVOCATION_TYPE")
if invocation_type == "COMPOSE":

    MYSQL_USER = get_env_variable("MYSQL_USER")
    MYSQL_PASS = get_env_variable("MYSQL_PASS")
    MYSQL_HOST = get_env_variable("MYSQL_HOST")
    MYSQL_PORT = get_env_variable("MYSQL_PORT")
    MYSQL_DATABASE = get_env_variable("MYSQL_DATABASE")

    # The SQLAlchemy connection string.
    SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s:%s/%s" % (
        MYSQL_USER,
        MYSQL_PASS,
        MYSQL_HOST,
        MYSQL_PORT,
        MYSQL_DATABASE,
    )
elif invocation_type == "RUN":
    SQLALCHEMY_DATABASE_URI = get_env_variable("DB_URL")
else:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(DATA_DIR, "superset.db")

REDIS_HOST = ""
REDIS_PORT = ""
REDIS_PASSWORD = ""  # nosec
if invocation_type == "COMPOSE":
    REDIS_HOST = get_env_variable("REDIS_HOST")
    REDIS_PORT = get_env_variable("REDIS_PORT")
    REDIS_PASSWORD = get_env_variable("REDIS_PASSWORD")
    RESULTS_BACKEND = RedisCache(
        host=REDIS_HOST,
        port=REDIS_PORT,
        key_prefix="superset_results",
        password=REDIS_PASSWORD,
    )
elif invocation_type == "RUN":
    REDIS_PASSWORD = get_env_variable("REDIS_URL").split(":")[2].split("@")[0]
    REDIS_HOST = get_env_variable("REDIS_URL").split("@")[1].split(":")[0]
    REDIS_PORT = get_env_variable("REDIS_URL").split(":")[3].replace("/0", "")
    RESULTS_BACKEND = RedisCache(
        host=REDIS_HOST,
        port=REDIS_PORT,
        key_prefix="superset_results",
        password=REDIS_PASSWORD,
    )
else:
    RESULTS_BACKEND = None


class CeleryConfig:
    """Contains Celery configs for Superset"""

    BROKER_URL = (
        "redis://:%s@%s:%s/0" % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
        "sqla+sqlite:///" + os.path.join(DATA_DIR, "celeryDB.db"),
    )[bool(not REDIS_HOST)]
    CELERY_RESULT_BACKEND = (
        "redis://:%s@%s:%s/0" % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT),
        "db+sqlite:///" + os.path.join(DATA_DIR, "celeryResultDB.db"),
    )[bool(not REDIS_HOST)]
    CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"}}
    CELERY_IMPORTS = ("superset.sql_lab",)
    CELERY_TASK_PROTOCOL = 1


CELERY_CONFIG = CeleryConfig  # pylint: disable=invalid-name

WTF_CSRF_ENABLED = False


class ReverseProxied:
    """Reverse Proxy for Superset"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        return self.app(environ, start_response)


ADDITIONAL_MIDDLEWARE = [
    ReverseProxied,
]

APP_ICON = "/nexa/static_nexa/images/nexa_superset_logo.png"
