import requests

URL_SEND_MESSAGE = 'https://api.telegram.org/bot{token}/sendMessage'
URL_GET_UPDATES = 'https://api.telegram.org/bot{token}/getUpdates'
URL_SEND_PHOTO = 'https://api.telegram.org/bot{token}/sendPhoto'


class BaseBot:
    def __init__(self, token):
        self.token = token
        self.session = requests.session()

    def get_updates(self, offset=None, limit=None, timeout=1, allowed_updates=None):
        url = URL_GET_UPDATES.format(token=self.token)
        body = {'timeout': timeout}
        if offset:
            body['offset'] = offset
        if limit:
            body['limit'] = limit
        if allowed_updates:
            body['allowed_updates'] = allowed_updates
        r = self.session.post(url=url, json=body)
        return r.json()

    def send_message(self, chat_id, text, parse_mode=None, disable_web_page_preview=None):
        url = URL_SEND_MESSAGE.format(token=self.token)
        body = {'chat_id': chat_id,
                'text': text}
        if parse_mode:
            body['parse_mode'] = parse_mode
        if disable_web_page_preview is not None:
            body['disable_web_page_preview'] = bool(disable_web_page_preview)
        r = self.session.post(url=url, json=body)
        return r.json()

    def send_photo(self, chat_id, photo, caption=None, parse_mode=None):
        url = URL_SEND_PHOTO.format(token=self.token)
        body = {'chat_id': chat_id}
        if caption:
            body['caption'] = caption
        if parse_mode:
            body['parse_mode'] = parse_mode
        if isinstance(photo, bytes):
            r = self.session.post(url=url, files={'photo': photo}, params=body)
        else:
            body['photo'] = photo
            r = self.session.post(url=url, json=body)
        return r.json()
