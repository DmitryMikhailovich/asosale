import sqlite3
import datetime
from abstract_storage import AbstractStorage
from process_status import ProcessStatus
from converters import sqlite_timestamp_converter, sqlite_timestamp_adapter


sqlite3.register_adapter(datetime.datetime, sqlite_timestamp_adapter)
sqlite3.register_converter('datetime', sqlite_timestamp_converter)


class SqliteStorage(AbstractStorage):
    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.db = sqlite3.connect(str(config.get_storage_path()), detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row

        self.sql_path = self.config.get_sql_scripts_path()

        self.sql_stage_product = self.get_script_text('insert_products_stg')
        self.sql_stage_product_alt_names = self.get_script_text('insert_product_alt_names_stg')
        self.sql_stage_product_web_categories = self.get_script_text('insert_product_web_categories_stg')
        self.sql_stage_price = self.get_script_text('insert_prices_stg')

    def get_script_text(self, script_name):
        if not script_name.endswith('.sql'):
            script_name += '.sql'
        with self.sql_path.joinpath(script_name).open() as f:
            return f.read()

    def update_bot_params(self, last_sale_id, upd_offset, new_chats):
        self.db.execute(self.get_script_text('update_bot_upd_offset'), [upd_offset])
        self.db.execute(self.get_script_text('update_bot_last_sale_id'), [last_sale_id])
        if new_chats:
            self.db.executemany(self.get_script_text('insert_chats'), new_chats)
        self.db.commit()

    def get_chat_ids(self):
        sql = self.get_script_text('select_chat_ids')
        return set(row[0] for row in self.db.execute(sql).fetchall())

    def get_bot_upd_offset(self):
        sql = self.get_script_text('select_bot_upd_offset')
        return int(self.db.execute(sql).fetchone()[0])

    def get_bot_last_sale_id(self):
        sql = self.get_script_text('select_bot_last_sale_id')
        return int(self.db.execute(sql).fetchone()[0])

    def get_last_process_status(self):
        sql = self.get_script_text('select_last_process_status')
        row = self.db.execute(sql).fetchone()
        if not row:
            return None
        return ProcessStatus(process_id=row['process_id'],
                             start_dtm=row['start_dtm'],
                             end_dtm=row['end_dtm'],
                             status=row['status'],
                             cnt=row['cnt'])

    def log_new_process(self, start_dtm):
        ps = ProcessStatus(process_id=None, start_dtm=start_dtm)
        sql = self.get_script_text('insert_log_processes')
        self.db.execute(sql, ps.get_as_json())
        ps = self.get_last_process_status()
        self.db.commit()
        return ps

    def update_process_status(self, process_status):
        sql = self.get_script_text('update_process_status')
        self.db.execute(sql, process_status.get_as_json())
        self.db.commit()

    def truncate_stage(self):
        sql = self.get_script_text('truncate_stg')
        self.db.executescript(sql)
        self.db.commit()

    def get_stg_product_ids(self):
        # TODO: wrap in script
        rows = self.db.execute('select id from products_stg').fetchall()
        return set(row[0] for row in rows)

    def get_products_lastmod(self):
        # TODO: wrap in script
        rows = self.db.execute('select id, lastmod from products').fetchall()
        return dict((row[0], row[1]) for row in rows)

    def stage_product(self, asos_product):
        self.db.execute(self.sql_stage_product, asos_product.get_product_stg_json())
        self.db.executemany(self.sql_stage_product_alt_names, asos_product.get_alt_names_json())
        self.db.executemany(self.sql_stage_product_web_categories, asos_product.get_web_categories_json())
        if asos_product.asos_price:
            self.stage_price(asos_product.asos_price)
        else:
            self.db.commit()

    def stage_price(self, asos_price):
        self.db.execute(self.sql_stage_price, asos_price.get_price_json())
        self.db.commit()

    def load_stage_into_storage(self):
        sql = self.get_script_text('load_to_storage')
        self.db.executescript(sql)
        self.db.commit()

    def fetch_new_sales(self, last_sale_id):
        sql = self.get_script_text('select_new_sales')
        return self.db.execute(sql, [last_sale_id]).fetchall()

    def close(self):
        if 'db' in dir(self) and self.db:
            self.db.close()
