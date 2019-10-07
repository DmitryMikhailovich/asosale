from asos_price import AsosPrice


class AsosProduct:
    def __init__(self, url, lastmod, product_obj):
        self.url = url
        self.lastmod = lastmod
        self.id = product_obj['id']
        self.name = product_obj['name']
        alternate_names = product_obj.get('alternateNames', [])
        self.names = {al['locale']: al['title'] for al in alternate_names}
        self.gender = product_obj.get('gender', 'NA')
        self.code = product_obj.get('productCode', 'NA')
        brand = product_obj.get('brand', dict())
        self.brand_id = brand.get('brandId', -1)
        self.brand_name = brand.get('name', '')
        web_categories = product_obj.get('webCategories', [])
        self.web_category_ids = [wc['id'] for wc in web_categories]
        if 'price' in product_obj:
            self.asos_price = AsosPrice(product_id=self.id,
                                        lastmod=lastmod,
                                        price_obj=product_obj['price'])
        else:
            self.asos_price = None
        self.img_url = ''
        media = product_obj.get('media', dict())
        images = media.get('images', list())
        if images:
            self.img_url = images[0]['url']

    def get_product_stg_json(self):
        return {'id': self.id,
                'url': self.url,
                'lastmod': self.lastmod,
                'name': self.name,
                'gender': self.gender,
                'code': self.code,
                'brand_id': self.brand_id,
                'brand_name': self.brand_name,
                'img_url': self.img_url}

    def get_alt_names_json(self):
        return [{'product_id': self.id,
                'locale': k,
                 'name': v} for k, v in self.names.items()]

    def get_web_categories_json(self):
        return [{'product_id': self.id,
                 'web_category_id': cid} for cid in self.web_category_ids]
