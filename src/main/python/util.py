import os.path
import sys

from PyQt5.QtGui import QImage, QPixmap, QIcon
from fbs_runtime.application_context.PyQt5 import ApplicationContext


def get_fbs_resource(app_ctx: ApplicationContext, dir_name, res_name):
    file = os.path.join(dir_name, res_name)
    path = app_ctx.get_resource(file)
    print(path)
    return path


def client_secret(app_ctx):
    return get_fbs_resource(app_ctx, 'secret', 'client_secret.json')


def token_dest():
    return os.path.join(get_data_dir(), 'token.json')


def app_logo(app_ctx):
    logo = QIcon()
    if sys.platform == "win32":
        logo = get_QIcon(app_ctx, 'logo_win.png')
    elif sys.platform == "darwin":
        logo = get_QIcon(app_ctx, 'logo_mac.png')
    elif sys.platform == "linux":
        logo = get_QIcon(app_ctx, 'logo_mac.png')
    return logo


def get_data_dir():
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        home = os.path.join(home, 'AppData', 'Roaming')
    elif sys.platform == "linux":
        home = os.path.join(home, '.local', 'share')
    elif sys.platform == "darwin":
        home = os.path.join(home, 'Library', 'Application Support')
    print(home)
    home = os.path.join(home, 'Ephemeris')
    if not os.path.isdir(home):
        os.mkdir(home)
    return home


def get_QImage(app_ctx, res_name):
    return QImage(get_fbs_resource(app_ctx, 'res', res_name))


def get_QPixmap(app_ctx, res_name):
    return QPixmap(get_fbs_resource(app_ctx, 'res', res_name))


def get_QIcon(app_ctx, res_name):
    return QIcon(get_fbs_resource(app_ctx, 'res', res_name))
