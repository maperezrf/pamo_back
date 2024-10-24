from apps.master_price.models import MainProducts, SopifyProducts
from apps.master_price.conecctions_shopify import ConnectionsShopify
from apps.master_price.graphiqL_queries import GET_COST_PRODUCT

# def update_or_create_main_product(product_json):
#     con = ConnectionsShopify()
#     id_product = product_json['id']
#     title = product_json['title']
#     tags = product_json['tags']
#     vendor = product_json['vendor']
#     status = product_json['status']
#     variants = product_json['variants']
#     try:
#         category = product_json['category']['full_name']
#     except:
#         category = 'Sin categoría'
#     for i in range(len(variants)):
#         id_variant = variants[i]['id']
#         response = con.request_graphql(GET_COST_PRODUCT.format( id=f'gid://shopify/ProductVariant/{id_variant}'))
#         object, created = MainProducts.objects.get_or_create(id_variantShopi = id_variant)
#         object.id_product = id_product
#         object.title = title
#         object.tags = tags
#         object.vendor = vendor
#         object.status = status
#         object.id_variantShopi = id_variant
#         object.price = variants[i]['price']
#         object.compare_at_price = variants[i]['compare_at_price']
#         object.sku = variants[i]['sku']
#         object.barcode = variants[i]['barcode']
#         object.inventory_quantity = variants[i]['inventory_quantity']
#         try:
#             object.costo =  float(response.json()['data']['productVariant']['inventoryItem']['unitCost']['amount'])
#         except:
#             pass
#         try:
#             object.image_link = product_json['images'][0]['src']
#         except:
#             pass
#         object.category = category
#         object.save()
    
def delete_main_product(product_json):
    print(product_json)
    # item = MainProducts.objects.filter(id_product = f'gid://shopify/Product/{product_json['id']}' )
    # for i in item:
    #     i.delete()


def update_or_create_main_product(products):
        
        for index, product in enumerate(products):
            for i in product['variant']:
                print(i)
                print(product)
                try:
                    index += 1
                    element, created = MainProducts.objects.get_or_create(id_product = product['product_id']['id'], id_variantShopi = i['id'], sku = i['sku'] )
                    print(element)
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        element = MainProducts()
                        element.id_product = product['product_id']
                        element.id_variantShopi = i['id']
                        element.sku = f'duplicidad sku:{i["sku"]} indice:{index}'
                element.title = product['product_id']['title']
                element.cost = i['inventoryItem']['unitCost']['amount'] if  i['inventoryItem']['unitCost'] else 0
                element.packaging_cost = (2765 + ((element.items_number-1)*623))
                element.image_link = product['image']['src'] if 'image' in product else 'sin imagen'
                element.inventory_quantity = i['inventoryQuantity']
                element.save()
                item, relation_created  = SopifyProducts.objects.get_or_create(MainProducts = element)
                item.tags = product['product_id']['tags']
                item.vendor = product['product_id']['vendor']
                item.status = product['product_id']['status']
                item.real_price = i['price']
                item.compare_at_price = i['compareAtPrice']
                item.barcode = i['barcode']
                item.category = product['product_id']['category']['fullName'] if product['product_id']['category'] else 'Sin Categoria'
                item.save()