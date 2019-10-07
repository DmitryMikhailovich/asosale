import io
import traceback
from base_bot import BaseBot
from config import Config

_instance = None

# TODO: move to separate project
class AdminBot(BaseBot):
    @staticmethod
    def get_instance():
        global _instance
        if not _instance:
            config = Config()
            _instance = AdminBot(config)
        return _instance

    def __init__(self, config):
        super().__init__(config.get_admin_bot_token())
        self.admin_chat_id = config.get_admin_chat_id()

    def log(self, app, message):
        message = message.replace('<', '&lt;').replace('>', '&gt;')
        text = '<b>[{}]</b> {}'.format(app.upper(), message)
        self.send_message(self.admin_chat_id, text, parse_mode='HTML')

    def log_error(self, app, exc_info):
        buf = io.StringIO('An exception occurred:\n')
        traceback.print_exception(*exc_info, file=buf)
        self.log(app, buf.getvalue())
