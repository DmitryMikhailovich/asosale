SELECT sale_id
    , url
    , img_url
    , gender
    , name
    , brand_name
    , currency
    , current_price
    , previous_price
FROM new_sales
WHERE sale_id > ?;