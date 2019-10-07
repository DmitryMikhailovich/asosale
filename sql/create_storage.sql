DROP TABLE IF EXISTS products;

CREATE TABLE products
(
    id INTEGER PRIMARY KEY
    , lastmod DATETIME
    , url TEXT
    , name TEXT
    , gender TEXT
    , code TEXT
    , brand_id INTEGER
    , img_url TEXT
)
;

DROP TABLE IF EXISTS products_stg;

CREATE TABLE products_stg
(
    id INTEGER
    , lastmod DATETIME
    , url TEXT
    , name TEXT
    , gender TEXT
    , code TEXT
    , brand_id INTEGER
    , brand_name TEXT
    , img_url TEXT
)
;

DROP TABLE IF EXISTS brands;

CREATE TABLE brands
(
    id INTEGER PRIMARY KEY
    , name TEXT
)
;


DROP TABLE IF EXISTS product_alt_names;

CREATE TABLE product_alt_names
(
    product_id INTEGER
    , locale TEXT
    , name TEXT
    , PRIMARY KEY (product_id, locale)
)
;

DROP TABLE IF EXISTS product_alt_names_stg;

CREATE TABLE product_alt_names_stg
(
    product_id INTEGER
    , locale TEXT
    , name TEXT
)
;


DROP TABLE IF EXISTS product_web_categories;

CREATE TABLE product_web_categories
(
    product_id INTEGER
    , web_category_id INTEGER
)
;

DROP TABLE IF EXISTS product_web_categories_stg;

CREATE TABLE product_web_categories_stg
(
    product_id INTEGER
    , web_category_id INTEGER
)
;


DROP TABLE IF EXISTS prices;

CREATE TABLE prices
(
    price_id INTEGER PRIMARY KEY
    , product_id INTEGER
    , lastmod DATETIME
    , currency TEXT
    , current_price REAL
    , previous_price REAL
)
;

DROP TABLE IF EXISTS prices_stg;

CREATE TABLE prices_stg
(
    product_id INTEGER
    , lastmod DATETIME
    , currency TEXT
    , current_price REAL
    , previous_price REAL
)
;

DROP TABLE IF EXISTS updated_prices;

CREATE TABLE updated_prices
(
    product_id INTEGER
    , lastmod DATETIME
    , currency TEXT
    , current_price REAL
    , previous_price REAL
)
;


DROP TABLE IF EXISTS new_sales;

CREATE TABLE new_sales
(
      sale_id INTEGER PRIMARY KEY
    , product_id INTEGER
    , lastmod DATETIME
    , url TEXT
    , img_url TEXT
    , gender TEXT
    , name TEXT
    , brand_name TEXT
    , currency TEXT
    , current_price REAL
    , previous_price REAL
);


DROP TABLE IF EXISTS params;

CREATE TABLE params
(
    param_key TEXT PRIMARY KEY
    , timestamp_value DATETIME
    , int_value INTEGER
    , text_value TEXT
)
;

DROP TABLE IF EXISTS log_processes;

CREATE TABLE log_processes
(
    process_id INTEGER PRIMARY KEY
    , start_dtm DATETIME
    , end_dtm DATETIME
    , status TEXT
    , cnt INTEGER
);


DROP TABLE IF EXISTS chats;

CREATE TABLE chats
(
    id INTEGER PRIMARY KEY
    , first_name TEXT
    , username TEXT
);

INSERT INTO params (param_key, int_value)
VALUES ('BOT_UPD_OFFSET', 0);

INSERT INTO params (param_key, int_value)
VALUES ('BOT_LAST_SALE_ID', 0);
