from apps.master_price.models import MainProducts

def update_or_create_main_product(product_json):
    id_product = product_json['id']
    title = product_json['title']
    tags = product_json['tags']
    vendor = product_json['vendor']
    status = product_json['status']
    variants = product_json['variants']
    category = product_json['category']['full_name']
    for i in  range(variants.shape[0]):
        object, created = MainProducts.objects.get_or_create(i['id'])
        # if created:
        object.id_product = id_product
        object.title = title
        object.tags = tags
        object.vendor = vendor
        object.status = status
        object.id_variantShopi = i['id']
        object.price = i['price']
        object.compare_at_price = i['compare_at_price']
        object.sku = i['sku']
        object.barcode = i['barcode']
        object.inventory_quantity = i['inventory_quantity']
        # object.costo = 
        try:
            object.image_link = product_json['images'][0]['src']
        except:
            object.image_link = 'sin imagen'
        object.category = category
