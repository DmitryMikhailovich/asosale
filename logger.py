import sys
import traceback
from admin_bot import AdminBot
from config import Config

_config = Config()
_adm_bot = AdminBot(_config.get_admin_bot_token(), _config.get_admin_chat_id())

#TODO: OOP may be?
def log_exception():
    exc_info = sys.exc_info()
    traceback.print_exception(*exc_info, file=sys.stderr)
    _adm_bot.log_error('ASOSALE', exc_info)


def log_message(msg):
    print(msg, file=sys.stderr)
    _adm_bot.log('ASOSALE', msg)
