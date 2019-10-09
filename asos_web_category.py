class AsosWebCategory:
    def __init__(self, web_category_obj, parent_id, lastmod):
        self.lastmod = lastmod
        self.parent_id = parent_id
        self.id = web_category_obj.get('id')
        self.name = web_category_obj.get('friendlyName')
        self.type = web_category_obj.get('type')
        self.url = web_category_obj.get('linkUrl')
        self.product_path = web_category_obj.get('productPath')

    def get_web_category_json(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'lastmod': self.lastmod,
            'name': self.name,
            'type': self.type,
            'url': self.url,
            'product_path': self.product_path,
        }

    @staticmethod
    def from_root_web_category_obj(root_web_category_obj, parent_id, lastmod):
        asos_web_category = AsosWebCategory(root_web_category_obj, parent_id, lastmod)
        new_parent_id = asos_web_category.id
        result = [asos_web_category]
        for child_web_category_obj in root_web_category_obj.get('categories', []):
            result.extend(AsosWebCategory.from_root_web_category_obj(child_web_category_obj, new_parent_id, lastmod))
        return result
