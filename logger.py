import sys
import traceback
from admin_bot import AdminBot

_adm_bot = AdminBot.get_instance()

#TODO: OOP may be?
def log_exception():
    exc_info = sys.exc_info()
    traceback.print_exception(*exc_info, file=sys.stderr)
    _adm_bot.log_error('ASOSALE', exc_info)


def log_message(msg):
    print(msg, file=sys.stderr)
    _adm_bot.log('ASOSALE', msg)
