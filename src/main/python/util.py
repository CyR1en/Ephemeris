import os.path
import pathlib
import sys

from PyQt5.QtGui import QImage, QPixmap, QIcon
from fbs_runtime.application_context.PyQt5 import ApplicationContext


def get_resource(app_ctx: ApplicationContext, res_name):
    print(os.getcwd())
    path = app_ctx.get_resource(res_name)
    print(path)
    return path


def client_secret(app_ctx):
    return get_resource(app_ctx, 'client_secret.json')


def token_dest():
    return os.path.join(get_data_dir(), 'ephemeris-token.json')


def get_data_dir() -> pathlib.Path:
    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


def secret(file_name):
    path = os.path.join(os.getcwd(), 'secret', file_name)
    return path


def get_QImage(app_ctx, res_name):
    return QImage(get_resource(app_ctx, res_name))


def get_QPixmap(app_ctx, res_name):
    return QPixmap(get_resource(app_ctx, res_name))


def get_QIcon(app_ctx, res_name):
    return QIcon(get_resource(app_ctx, res_name))
