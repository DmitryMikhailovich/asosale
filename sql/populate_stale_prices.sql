DELETE FROM stale_prices;

INSERT INTO stale_prices
(
      price_id
    , product_id
    , lastmod
    , currency
    , current_price
    , previous_price
)
SELECT
      price_id
    , product_id
    , lastmod
    , currency
    , current_price
    , previous_price
FROM (
    SELECT
          price_id
        , product_id
        , lastmod
        , currency
        , current_price
        , previous_price
        , row_number() OVER (PARTITION BY product_id ORDER BY lastmod DESC) AS rn
    FROM prices
) p
WHERE p.rn = 1
ORDER BY p.lastmod ASC
LIMIT 4000
;