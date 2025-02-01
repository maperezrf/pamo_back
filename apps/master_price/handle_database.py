from apps.master_price.models import MainProducts, SopifyProducts, ProductsMelonn, ProductsFalabella
from apps.master_price.conecctions_shopify import ConnectionsShopify
from apps.master_price.Connections_falabella import ConnectionFalabella
from apps.master_price.connections_melonn import connMelonn
from apps.master_price.graphiqL_queries import GET_COST_PRODUCT
import pandas as pd

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
    item = MainProducts.objects.filter(id_product = 'gid://shopify/Product/'+ str(product_json['id'] ))
    for i in item:
        i.delete()

def update_or_create_main_product(products):
        count = 0
        for product in products:
            for i in product['variant']:
                count += 1
                element, created = MainProducts.objects.get_or_create(id_product = product['product_id']['id'], id_variantShopi = i['id'], sku = str(i['sku']).upper().strip() if i['sku'] else f'{i["sku"]} indice:{count}')
                element.title = product['product_id']['title']
                element.cost = i['inventoryItem']['unitCost']['amount'] if  i['inventoryItem']['unitCost'] else 0
                element.packaging_cost = (2765 + ((element.items_number-1)*623))
                element.image_link = product['image']['src'] if 'image' in product else 'sin imagen'
                element.save()
                item, relation_created = SopifyProducts.objects.get_or_create(MainProducts = element)
                item.tags = product['product_id']['tags']
                item.vendor = product['product_id']['vendor']
                item.status = product['product_id']['status']
                item.real_price = i['price']
                item.compare_at_price = i['compareAtPrice']
                item.barcode = i['barcode']
                item.category = product['product_id']['category']['fullName'] if product['product_id']['category'] else 'Sin Categoria'
                item.save()

def set_inventory():
    con_m = connMelonn()
    products_melonn = con_m.get_inventory()
    products_missing = []
    for i in products_melonn:
        try:
            product = MainProducts.objects.get(sku = i['sku'].upper().strip() )
            product.inventory_quantity = i['inventoryByWarehouse'][0]['availableQuantity']
            product.save()
        except Exception as e:
            if "MainProducts matching query does not exist." in str(e):
                print('no encontrado')
                print( i['sku'].upper().strip())
                products_missing.append(i['sku'])
    df = pd.DataFrame(products_missing, columns=['sku'])
    df.to_excel('faltante shopify.xlsx', index=False)

def set_products_melonn():
    con_m = connMelonn()
    products_melonn = con_m.get_inventory()
    skus_main_products = {p.sku: p for p in MainProducts.objects.filter(sku__in=[p['sku'] for p in products_melonn])}
    to_update = []
    to_create = []
    for i in products_melonn:
        main_p = skus_main_products.get(i['sku'])
        if main_p:
            item, created = ProductsMelonn.objects.get_or_create(MainProducts=main_p)
        else:
            item, created = ProductsMelonn.objects.get_or_create(internalCode=i['sku'])
        item.internalCode = i['internalCode']
        item.inventory_quantity = i['inventoryByWarehouse'][0]['availableQuantity']
        if created:
            to_create.append(item)
        else:
            to_update.append(item)
    if to_create:
        ProductsMelonn.objects.bulk_create(to_create)
    if to_update:
        ProductsMelonn.objects.bulk_update(to_update, ['internalCode', 'inventory_quantity'])
    print('Finaliza')

def set_products_falabella():
    con_f = ConnectionFalabella()
    response = con_f.request_falabella('GetProducts')
    products = response.json()['SuccessResponse']['Body']['Products']['Product']
    skus_main_products = {p.sku: p for p in MainProducts.objects.filter(sku__in=[p['SellerSku'] for p in products])}
    to_update = []
    for i in products:
        main_p = skus_main_products.get(i['SellerSku'])
        if main_p:
            item, created = ProductsFalabella.objects.get_or_create(MainProducts=main_p)
        else:
            item, created = ProductsFalabella.objects.get_or_create(ShopSku=i['ShopSku'])
        item.ShopSku = i['ShopSku']
        item.Url = i['Url']
        to_update.append(item)
    ProductsFalabella.objects.bulk_update(to_update, ['ShopSku', 'Url'])
    print('Finaliza')