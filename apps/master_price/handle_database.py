from apps.master_price.models import MainProducts
from apps.master_price.conecctions_shopify import ConnectionsShopify
from apps.master_price.graphiqL_queries import GET_COST_PRODUCT

def update_or_create_main_product(product_json):
    con = ConnectionsShopify()
    id_product = product_json['id']
    title = product_json['title']
    tags = product_json['tags']
    vendor = product_json['vendor']
    status = product_json['status']
    variants = product_json['variants']
    category = product_json['category']['full_name']
    for i in range(len(variants)):
        id_variant = variants[i]['id']
        response = con.request_graphql(GET_COST_PRODUCT.format( id=f'gid://shopify/ProductVariant/{id_variant}'))
        object, created = MainProducts.objects.get_or_create(id_variantShopi = id_variant)
        object.id_product = id_product
        object.title = title
        object.tags = tags
        object.vendor = vendor
        object.status = status
        object.id_variantShopi = id_variant
        object.price = variants[i]['price']
        object.compare_at_price = variants[i]['compare_at_price']
        object.sku = variants[i]['sku']
        object.barcode = variants[i]['barcode']
        object.inventory_quantity = variants[i]['inventory_quantity']
        try:
            object.costo =  float(response.json()['data']['productVariant']['inventoryItem']['unitCost']['amount'])
        except:
            pass
        try:
            object.image_link = product_json['images'][0]['src']
        except:
            pass
        object.category = category
        object.save()
    
def delete_main_product(product_json):
    item = MainProducts.objects.filter(id_product = 9212659958037 )
    for i in item:
        i.delete()

