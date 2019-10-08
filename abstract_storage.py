class AbstractStorage:
    def __init__(self, config=None, *args, **kwargs):
        raise NotImplementedError

    def get_last_process_status(self):
        raise NotImplementedError

    def log_new_process(self, from_dtm):
        raise NotImplementedError

    def update_process_status(self, process_status):
        raise NotImplementedError

    def get_ids_of_products_with_stale_prices(self):
        raise NotImplementedError

    def get_products_lastmod(self):
        raise NotImplementedError

    def get_stg_product_ids(self):
        raise NotImplementedError

    def truncate_stage(self):
        raise NotImplementedError

    def stage_product(self, asos_product):
        raise NotImplementedError

    def stage_price(self, asos_price):
        raise NotImplementedError

    def stage_prices(self, asos_prices):
        raise NotImplementedError

    def load_stage_into_storage(self):
        raise NotImplementedError

    def fetch_new_sales(self, last_sale_id):
        raise NotImplementedError

    def get_bot_last_sale_id(self):
        raise NotImplementedError

    def get_bot_upd_offset(self):
        raise NotImplementedError

    def get_chat_ids(self):
        raise NotImplementedError

    def update_bot_params(self, last_sale_id, upd_offset, new_chats):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def __del__(self):
        self.close()
