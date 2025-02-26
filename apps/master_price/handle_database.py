from apps.master_price.models import MainProducts, SopifyProducts
from apps.master_price.conecctions_shopify import ConnectionsShopify
from apps.master_price.connections_melonn import connMelonn
from apps.master_price.graphiqL_queries import GET_COST_PRODUCT
import pandas as pd

def delete_main_product(product_json):
    item = MainProducts.objects.filter(id_product = 'gid://shopify/Product/'+ str(product_json['id'] ))
    for i in item:
        i.delete()


def update_or_create_main_product(products):
    for index, product in enumerate(products):
        for i in product['variant']:
            index += 1
            try:
                element, created = MainProducts.objects.get_or_create(id_product = product['product_id']['id'], id_variantShopi = i['id'], sku = i['sku'] )
                if created:
                        element.id_product = product['product_id']
                        element.id_variantShopi = i['id']
                        element.sku = f'duplicidad sku:{i["sku"]} indice:{index}'
                element.title = product['product_id']['title']
                # element.cost = i['inventoryItem']['unitCost']['amount'] if  i['inventoryItem']['unitCost'] else 0
                element.packaging_cost = (2765 + ((element.items_number-1)*623))
                element.image_link = product['image']['src'] if 'image' in product else 'sin imagen'
                element.stock = i['inventoryQuantity']
                element.save()
                item, relation_created  = SopifyProducts.objects.get_or_create(MainProducts = element)
                item.tags = product['product_id']['tags']
                item.vendor = product['product_id']['vendor']
                item.status = product['product_id']['status']
                item.compare_at_price = i['compareAtPrice']
                item.barcode = i['barcode']
                item.category = product['product_id']['category']['fullName'] if product['product_id']['category'] else 'Sin Categoria'
                item.save()
            except Exception as e:
                 print(product['product_id']['id'])
                 print(i['id'])
                 print(i['sku'])
                 print(e)