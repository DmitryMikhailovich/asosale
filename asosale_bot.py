import sys
import signal
import datetime as dt
import time
from base_bot import BaseBot
from config import Config
from sqlite_storage import SqliteStorage
from converters import strike
from logger import log_message, log_exception


class AsosaleBot(BaseBot):
    def __init__(self, config):
        super().__init__(config.get_bot_token())
        self.db = SqliteStorage(config)
        self.last_sale_id = self.db.get_bot_last_sale_id()
        self.upd_offset = self.db.get_bot_upd_offset()
        self.chat_ids = self.db.get_chat_ids()
        self.new_chats = set()
        self.last_notification_dtm = None
        self.templates_path = config.get_templates_path()
        self.TMPL_NOTIF_CAPTION = self.get_template('notification_caption')
        self.TMPL_HELLO = self.get_template('hello_message')
        log_message('Bot has started')

    def get_template(self, template):
        with self.templates_path.joinpath(template).open() as f:
            return f.read()

    def run(self):
        while True:
            self.process_updates()
            if self.is_time_to_notify():
                self.send_notifications()
            time.sleep(1)

    def is_time_to_notify(self):
        if not self.last_notification_dtm:
            return True
        td = dt.datetime.now() - self.last_notification_dtm
        return td.seconds > 1800

    def process_updates(self):
        updates = self.get_updates(offset=self.upd_offset)
        if not updates['ok']:
            print('Failed to fetch updates')
            return
        updates = updates['result']
        for update in updates:
            self.upd_offset = update['update_id'] + 1
            try:
                message = update['message']
                text = message['text']
                if text == '/start':
                    self.add_new_chat(message['chat'])
            except:
                log_message('Failed to process update')
                log_exception()

    def send_notifications(self):
        self.last_notification_dtm = dt.datetime.now()
        if not self.chat_ids:
            return
        new_sales = self.db.fetch_new_sales(self.last_sale_id)
        if not new_sales:
            return
        new_last_sale_id = max(row['sale_id'] for row in new_sales)

        chat_ids = self.chat_ids.copy()
        random_chat_id = chat_ids.pop()
        for row in new_sales:
            caption = self.TMPL_NOTIF_CAPTION.format(brand_name=row['brand_name'],
                                                     gender=row['gender'],
                                                     name=row['name'],
                                                     url=row['url'],
                                                     current_price=round(row['current_price']),
                                                     previous_price=strike(round(row['previous_price'])),
                                                     currency=row['currency'],
                                                     currency_strike=strike(row['currency']))
            img_url = row['img_url']
            if img_url:
                try:
                    img_req = self.session.get('http://'+img_url)
                    img_content = img_req.content
                    msg_obj = self.send_photo(random_chat_id, img_content, caption, parse_mode='Markdown')
                    if msg_obj['ok']:
                        img_url = msg_obj['result']['photo'][0]['file_id']
                except:
                    log_message('Failed to download image {}'.format(row['img_url']))
                    log_exception()
                    img_url = None
            for chat_id in chat_ids:
                if img_url:
                    self.send_photo(chat_id, img_url, caption, parse_mode='Markdown')
                else:
                    self.send_message(chat_id, caption, parse_mode='Markdown')
        self.last_sale_id = new_last_sale_id

    def add_new_chat(self, chat_obj):
        chat_id = chat_obj['id']
        first_name = chat_obj.get('first_name')
        username = chat_obj.get('username')
        self.send_message(chat_id, self.TMPL_HELLO)
        self.new_chats.add((chat_id, first_name, username))
        self.chat_ids.add(chat_id)
        log_message('New user: {} ({}) with id {}'.format(username, first_name, chat_id))

    def destroy(self):
        self.db.update_bot_params(last_sale_id=self.last_sale_id,
                                  upd_offset=self.upd_offset,
                                  new_chats=self.new_chats)
        self.db.close()
        log_message('Bot is destroyed')


def get_sigterm_handler(bot):
    def sigterm_handler(sig, frame):
        bot.destroy()
        sys.exit(0)
    return sigterm_handler


if __name__ == '__main__':
    config = Config()
    bot = AsosaleBot(config)
    signal.signal(signal.SIGTERM, get_sigterm_handler(bot))
    bot.run()

