INSERT INTO prices_stg
(
    product_id
    , lastmod
    , currency
    , current_price
    , previous_price
)
VALUES (
    :product_id
    , :lastmod
    , :currency
    , :current_price
    , :previous_price
);