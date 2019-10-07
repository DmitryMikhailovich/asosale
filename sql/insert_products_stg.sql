INSERT INTO products_stg
(
    id
    , lastmod
    , url
    , name
    , gender
    , code
    , brand_id
    , brand_name
    , img_url
)
VALUES (:id
    , :lastmod
    , :url
    , :name
    , :gender
    , :code
    , :brand_id
    , :brand_name
    , :img_url
    );