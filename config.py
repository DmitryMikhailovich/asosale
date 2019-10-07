import json
from pathlib import Path

STORAGE_PATH = 'STORAGE_PATH'
SQL_SCRIPTS_PATH = 'SQL_SCRIPTS_PATH'
TEMPLATES_PATH = 'TEMPLATES_PATH'
BOT_TOKEN_PATH = 'BOT_TOKEN_PATH'
ADMIN_BOT_TOKEN_PATH = 'ADMIN_BOT_TOKEN_PATH'
ADMIN_CHAT_ID = 'ADMIN_CHAT_ID'


class Config:
    def __init__(self, path=None):
        if path:
            conf_path = Path(path)
        else:
            conf_path = Path(__file__).absolute().parent.joinpath('config.json')
        with conf_path.open() as f:
            self.conf = json.load(f)

    def get_storage_path(self):
        return Path(self.conf[STORAGE_PATH]).absolute()

    def get_sql_scripts_path(self):
        return Path(self.conf[SQL_SCRIPTS_PATH]).absolute()

    def get_templates_path(self):
        return Path(self.conf[TEMPLATES_PATH]).absolute()

    def get_bot_token(self):
        with Path(self.conf[BOT_TOKEN_PATH]).absolute().open() as f:
            return f.read()

    def get_admin_bot_token(self):
        with Path(self.conf[ADMIN_BOT_TOKEN_PATH]).absolute().open() as f:
            return f.read()

    def get_admin_chat_id(self):
        return self.conf[ADMIN_CHAT_ID]
