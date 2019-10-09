INSERT INTO web_categories_stg
(
      id
    , lastmod
    , parent_id
    , name
    , type
    , url
    , product_path
)
VALUES
(
      :id
    , :lastmod
    , :parent_id
    , :name
    , :type
    , :url
    , :product_path
);