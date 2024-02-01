import os
import getpass

ROOT_PATH = os.path.realpath(os.path.dirname(__file__))
APP_ICON_PATH = os.path.join(ROOT_PATH, 'resources', 'app_icon.ico')
CONFIG_PATH = os.path.join(ROOT_PATH, 'setup', 'config.json')
USER_NAME = getpass.getuser()