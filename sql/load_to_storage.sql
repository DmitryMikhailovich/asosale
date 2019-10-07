INSERT OR REPLACE INTO products
(
    id
    , lastmod
    , url
    , name
    , gender
    , code
    , brand_id
    , img_url
)
SELECT id
    , lastmod
    , url
    , name
    , gender
    , code
    , brand_id
    , img_url
FROM (
    SELECT
        id
        , lastmod
        , url
        , name
        , gender
        , code
        , brand_id
        , img_url
        , row_number() OVER (PARTITION BY id ORDER BY lastmod DESC) AS rn
    FROM products_stg
) t
WHERE rn=1;

INSERT OR REPLACE INTO brands
(
    id
    , name
)
SELECT
    brand_id
    , brand_name
FROM (
    SELECT
        brand_id
        , brand_name
        , row_number () OVER (PARTITION BY brand_id ORDER BY lastmod DESC) AS rn
    FROM products_stg
) t
WHERE rn=1;


DELETE FROM product_alt_names
WHERE product_id IN (SELECT product_id FROM product_alt_names_stg);

INSERT INTO product_alt_names
(
    product_id
    , locale
    , name
)
SELECT
    product_id
    , locale
    , name
FROM product_alt_names_stg;

DELETE FROM product_web_categories
WHERE product_id IN (SELECT product_id FROM product_web_categories_stg);

INSERT INTO product_web_categories
(
    product_id
    , web_category_id
)
SELECT
    product_id
    , web_category_id
FROM product_web_categories_stg;


DELETE FROM updated_prices;

INSERT INTO updated_prices
(
    product_id
    , lastmod
    , currency
    , current_price
    , previous_price
)
SELECT
      new_prices.product_id
    , new_prices.lastmod
    , new_prices.currency
    , new_prices.current_price
    , new_prices.previous_price
FROM (
    SELECT
          product_id
        , lastmod
        , currency
        , current_price
        , previous_price
        , row_number() OVER (PARTITION BY product_id, currency ORDER BY lastmod DESC) AS rn
    FROM prices_stg
) new_prices
LEFT JOIN
(
    SELECT
          product_id
        , currency
        , current_price
        , previous_price
        , row_number() OVER (PARTITION BY product_id, currency ORDER BY lastmod DESC) AS rn
    FROM prices

) stored_prices ON new_prices.product_id = stored_prices.product_id
               AND new_prices.currency = stored_prices.currency
               AND new_prices.rn=1
               AND stored_prices.rn=1
WHERE new_prices.current_price <> coalesce(stored_prices.current_price, -123)
   OR new_prices.previous_price <> coalesce(stored_prices.previous_price, -123)
;

INSERT INTO prices
(
    product_id
    , lastmod
    , currency
    , current_price
    , previous_price
)
SELECT
    product_id
    , lastmod
    , currency
    , current_price
    , previous_price
FROM updated_prices;

INSERT INTO new_sales
(
    product_id
    , lastmod
    , url
    , img_url
    , gender
    , name
    , brand_name
    , currency
    , current_price
    , previous_price
)
SELECT
    p.id
    , up.lastmod
    , p.url
    , p.img_url
    , p.gender
    , p.name
    , b.name
    , up.currency
    , up.current_price
    , up.previous_price
FROM updated_prices up
INNER JOIN products p ON p.id = up.product_id
INNER JOIN brands b ON b.id = p.brand_id
WHERE up.current_price < up.previous_price
AND up.product_id IN (SELECT product_id FROM prices GROUP BY product_id HAVING COUNT(*)>1);
