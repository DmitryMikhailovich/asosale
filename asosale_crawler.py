import re
import math
import requests
import time
import datetime as dt
from lxml import etree
from converters import parse_ts
from config import Config
from sqlite_storage import SqliteStorage
from asos_product import AsosProduct
from asos_price import AsosPrice
from asos_web_category import AsosWebCategory
from logger import log_exception, log_message

PRODUCT_IDS = 'productIds'
KEYSTORE_DATAVERSION = 'keyStoreDataversion'

SITEMAP_NS = {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

ROOT_SITEMAP_URL = 'https://www.asos.com/ru/product-sitemap-index-RU.xml'

ROOT_CATEGORY_IDS = [111, 1000, 1001]

STOCKPRICE_URL = 'https://www.asos.com/api/product/catalogue/v3/stockprice'

PRODUCTS_URL = 'https://www.asos.com/api/product/catalogue/v3/products/{pid}'

CATEGORIES_URL = 'https://www.asos.com/api/product/category/v1/categories/{cid}'

HEADERS = {
    "asos-c-name": "asos-web-productpage",
    "asos-c-version": "2.0.2658",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
}

STOCKPRICE_BASE_PARAMS = {
    "store": "RU",
    "currency": "RUB"
}

PRODUCT_BASE_PARAMS = {
    "store": "RU"
}

CATEGORY_BASE_PARAMS = {
    'Country': 'RU',
    'Lang': 'ru-RU'
}

PAT_PRD_URL = re.compile(r'\/prd\/(?P<product_id>\d+)$', re.I)

_session = requests.session()


def get(url, headers={}, params={}, exc_msg='Failed to GET {}'):
    retry_count = 0
    while True:
        r = _session.get(url, headers=headers, params=params)
        if r.status_code == 200:
            return r
        if r.status_code != 200:
            if retry_count > 2:
                raise requests.ConnectionError(exc_msg.format(url))
            retry_count += 1
            time.sleep(1.0)


def parse_root_sitemap(url):
    r = get(url, headers=HEADERS, exc_msg='Failed to get root sitemap {}')
    doc = etree.fromstring(r.content)
    urls = doc.xpath('//xmlns:sitemap/xmlns:loc/text()', namespaces=SITEMAP_NS)
    return urls


def get_product_urls_from_sitemap(url, products_lastmod):
    r = get(url, headers=HEADERS, exc_msg='Failed to get sitemap {}')
    doc = etree.fromstring(r.content)
    for url_el in doc.iter(tag='{*}url'):
        loc_el = url_el.find('{*}loc')
        lastmod_el = url_el.find('{*}lastmod')
        if loc_el is None or lastmod_el is None:
            continue
        url = loc_el.text
        prd_url_match = PAT_PRD_URL.search(url)
        if not prd_url_match:
            continue

        product_id = int(prd_url_match.group('product_id'))
        lastmod = parse_ts(lastmod_el.text)
        if product_id in products_lastmod and products_lastmod[product_id] >= lastmod:
            continue
        yield url, product_id, lastmod


def get_product_obj(product_id):
    r = get(PRODUCTS_URL.format(pid=str(product_id)), headers=HEADERS, params=PRODUCT_BASE_PARAMS, exc_msg='Failed to get product object {}')
    return r.json()


def get_stockprice_obj(product_ids):
    stockprice_params = STOCKPRICE_BASE_PARAMS.copy()
    stockprice_params[PRODUCT_IDS] = [str(pid) for pid in product_ids]
    r = get(STOCKPRICE_URL, headers=HEADERS, params=stockprice_params, exc_msg='Failed to get stockprice object')
    return r.json()


def get_web_categories_obj(cid):
    url = CATEGORIES_URL.format(cid=cid)
    r = get(url, headers=HEADERS, params=CATEGORY_BASE_PARAMS, exc_msg='Failed to get web categories for CID='+str(cid))
    return r.json()


def crawl_over_web_categories(storage, lastmod):
    for root_cid in ROOT_CATEGORY_IDS:
        try:
            web_categories_obj = get_web_categories_obj(root_cid)
            asos_web_categories = AsosWebCategory.from_root_web_category_obj(web_categories_obj['categories'], None, lastmod)
            storage.stage_web_categories(asos_web_categories)
        except requests.ConnectionError:
            log_exception()


def crawl_over_prices(storage, lastmod):
    ids_of_products_with_stale_prices = storage.get_ids_of_products_with_stale_prices()
    batch_size = 50
    for i in range(0, math.ceil(len(ids_of_products_with_stale_prices) / batch_size)):
        try:
            batch_with_product_ids = ids_of_products_with_stale_prices[i * batch_size:(i + 1) * batch_size]
            stockprice_objs = get_stockprice_obj(batch_with_product_ids)
            if not stockprice_objs:
                continue
            asos_prices = [AsosPrice.from_stockprice_obj(lastmod, so) for so in stockprice_objs]
            storage.stage_prices(asos_prices)
            time.sleep(0.25)
        except requests.ConnectionError:
            log_exception()


def crawl(storage):
    start_dtm = dt.datetime.now().astimezone(dt.timezone.utc)
    last_process_status = storage.get_last_process_status()

    if last_process_status and last_process_status.is_running():
        msg = 'Process with ID {} is still running. Finishing...'.format(last_process_status.process_id)
        log_message(msg)
        return
    if last_process_status and last_process_status.is_success() or not last_process_status:
        last_run_failed = False
        stg_product_ids = set()
        process_status = storage.log_new_process(start_dtm=start_dtm)
        storage.truncate_stage()
        storage.populate_stale_prices()
    if last_process_status and last_process_status.is_error():
        last_run_failed = True
        stg_product_ids = storage.get_stg_product_ids()
        process_status = last_process_status.copy()
        process_status.set_running()
        storage.update_process_status(process_status)
    msg = 'Process {} has started at {}. Last process status: *{}*'.format(process_status.process_id,
                                                                           start_dtm,
                                                                           last_process_status.status if last_process_status else 'NOT EXISTED')
    log_message(msg)

    try:
        if storage.need_to_update_web_categories():
            crawl_over_web_categories(storage, start_dtm)

        crawl_over_prices(storage, start_dtm)

        products_lastmod = storage.get_products_lastmod()
        sitemap_urls = parse_root_sitemap(ROOT_SITEMAP_URL)
        for sitemap_url in sitemap_urls:
            for url, product_id, lastmod in get_product_urls_from_sitemap(sitemap_url, products_lastmod):
                try:
                    if last_run_failed and product_id in stg_product_ids:
                        continue
                    product_obj = get_product_obj(product_id)
                    asos_product = AsosProduct(url, lastmod, product_obj)
                    storage.stage_product(asos_product)
                    process_status.cnt += 1
                    time.sleep(0.25)
                except requests.ConnectionError as e:
                    log_exception()
        #remove this when all img_urls are filled
        for url, product_id, lastmod in storage.db.execute('select url, id, lastmod from products where img_url is null and id in (select product_id from prices_stg) limit 300').fetchall():
            try:
                if last_run_failed and product_id in stg_product_ids:
                    continue
                
                product_obj = get_product_obj(product_id)
                asos_product = AsosProduct(url, lastmod, product_obj)
                storage.db.execute(storage.sql_stage_product, asos_product.get_product_stg_json())
                process_status.cnt += 1
                time.sleep(0.25)
            except requests.ConnectionError as e:
                log_exception()
        storage.db.commit()
        #block finish
        storage.load_stage_into_storage()
        process_status.end_dtm = dt.datetime.now().astimezone(dt.timezone.utc)
        process_status.set_succeeded()
    except Exception as e:
        log_exception()
        process_status.set_error()
    finally:
        storage.update_process_status(process_status)
        storage.close()
        msg = 'Process {} finished with status *{}* on {}. Updated products: {}'.format(process_status.process_id,
                                                                  process_status.status,
                                                                  dt.datetime.now().astimezone(dt.timezone.utc),
                                                                  process_status.cnt)
        log_message(msg)


if __name__ == '__main__':
    config = Config()
    storage = SqliteStorage(config)
    crawl(storage)
