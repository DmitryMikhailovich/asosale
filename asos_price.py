class AsosPrice:
    def __init__(self, product_id, lastmod, price_obj):
        self.product_id = product_id
        self.lastmod = lastmod
        self.currency = price_obj['currency']
        self.current_price = price_obj['current']['value']
        self.previous_price = price_obj['previous']['value']

    @staticmethod
    def from_stockprice_obj(lastmod, stockprice_obj):
        product_id = stockprice_obj['productId']
        price_obj = stockprice_obj['productPrice']
        return AsosPrice(product_id=product_id,
                         lastmod=lastmod,
                         price_obj=price_obj)

    def get_price_json(self):
        return {'product_id': self.product_id,
                'lastmod': self.lastmod,
                'currency': self.currency,
                'current_price': self.current_price,
                'previous_price': self.previous_price}
