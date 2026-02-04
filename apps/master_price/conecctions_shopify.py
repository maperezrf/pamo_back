from pamo_back.constants import *
import requests
import pandas as pd
import json
import os
from datetime import datetime
from pamo_back.queries  import GET_VARIANT_ID, GET_INVENTORY
import time
import json 
from pamo_back.queries import REQUEST_FINISH_BULK, CREATION_BULK
from apps.master_price.models import MainProducts, SopifyProducts, StatusProcess
from collections import defaultdict
from apps.master_price.utils import read_seets, update_status_bot, handle_init_process

class ConnectionsShopify():

    headers_shopify = {}
    orders = pd.DataFrame()

    def __init__(self) -> None:
        self.headers_shopify = {'X-Shopify-Access-Token' : ACCES_TOKEN, 'Content-Type' : 'application/json'}
        self.item = StatusProcess.objects.get_or_create(name = 'shopify_update')[0]

    def set_orders_df(self, orders):
        self.orders = orders

    def request_graphql(self, query, variables = None ):
        return requests.post(URL_GRAPHQL, headers=self.headers_shopify, data=json.dumps({"query": query, 'variables': variables}))

    def get_rest(self,url):
        return requests.get(url, headers= self.headers_shopify)

    def get_variant_id(self):
        sku_un = self.orders['SKU'].unique()
        for i in sku_un:
            query = GET_VARIANT_ID.format(skus = str(i).strip())
            response = requests.post(URL_GRAPHQL, headers=self.headers_shopify, data=json.dumps({"query": query}))
            try:
                variant_id = str(response.json()['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['id']).replace('gid://shopify/ProductVariant/', '')
                self.orders.loc[self.orders['SKU']==i, 'variant_id'] = variant_id
            except:
                print(f'No se encontro el SKU en shopify: {i}')
        return self.orders.loc[self.orders['variant_id'].notna()]

    def bucle_request(self, query, datatype):
        response = self.request_graphql(query.format(cursor=''))
        print(query.format(cursor=''))
        print(response.json())
        res  = response.json()['data'][datatype]['edges']
        print(res)
        daft_orders = make_json(res)
        print(daft_orders)
        has_next = response.json()['data'][datatype]['pageInfo']['hasNextPage']
        while has_next:
            response = self.request_graphql(query.format( cursor= f",after:\"{response.json()['data'][datatype]['pageInfo']['endCursor']}\""))
            res  = response.json()['data'][datatype]['edges']
            daft_orders.extend(make_json(res))
            has_next = response.json()['data'][datatype]['pageInfo']['hasNextPage']
        print(response.json())

    def create_orders(self):
        orders_gb = self.orders.groupby('ORDEN_COMPRA').agg({'variant_id':list, 'CANTIDAD_SKU':list,'COSTO_SKU':list}).reset_index()
        print(orders_gb.shape[0])
        print(len(orders_gb))
        data_log = {}
        data_log['success'] = []
        data_log['error'] = []
        for i in range(len(orders_gb)):   
            products = []
            oc = orders_gb.iloc[i]['ORDEN_COMPRA']
            cantidad = orders_gb.iloc[i]['CANTIDAD_SKU']
            costo = orders_gb.iloc[i]['COSTO_SKU']
            variant_id = orders_gb.iloc[i]['variant_id']
            products = []    
            for i in range(len(variant_id)):
                products.append({"variant_id": variant_id[i], "quantity": cantidad[i], "price": costo[i]})
                data = {
                    "order": {
                        "line_items": products,
                        "customer": {
                            "id": 7247084421397
                        },
                        "financial_status": "pending",
                        "note": f"orden de compra: {oc}"
                    }
                }
                try:  
                    response = requests.post(URL_CREATE_ORDERS, headers= self.headers_shopify, json = data)
                    if response.status_code == 201:
                        data_log['success'].append(oc)
                except:
                    data_log['error'].append(oc)
        return data_log
    
    def get_orders(self):
        return self.orders
    
    def get_inventory(self, df):
        for i in range(10):#udf.shape[0]):
            print(df.iloc[i].sku)
            response =  self.request_graphql(GET_INVENTORY.format(sku = df.iloc[i].sku))
            try:
                inventory = response.json()['data']['products']['edges'][0]['node']['variants']['edges'][0]['node']['inventoryQuantity']
                df.loc[i,'stock_shopyfi']= inventory
                print(response.json())
            except Exception as e:
                print(f'No se encontro el SKU: {df.iloc[i].sku}')
                df.loc[i,'stock_shopyfi']= 'El SKU no se encontró'
        return df.loc[df['existencia'] != df['stock_shopyfi']]
    
    def get_all_products(self):
        handle_init_process(self.item, True)
        self.request_graphql(CREATION_BULK)
        status = 'RUNNING'
        update_status_bot(self.item, progress = 5, status = 'Obteniendo Productos' )
        while status == 'RUNNING':
            response_bulk = self.request_graphql(REQUEST_FINISH_BULK)
            status = response_bulk.json()['data']['currentBulkOperation']['status']
            print(status)
            if status == 'RUNNING':
                time.sleep(10)
        response_bulk.json()
        file = requests.get(response_bulk.json()['data']['currentBulkOperation']['url'])
        json_lines = file.text.strip().split('\n')
        self.products = []
        json_lines = [json.loads(i) for i in json_lines]
        current_product = None
        current_variant = None
        for line in json_lines:
            if '__parentId' not in line:
                # New product
                if current_product:
                    self.products.append(current_product)
                current_product = line.copy()
                current_product['variants'] = []
                current_product['images'] = []
                current_variant = None
            elif 'ProductVariant' in line.get('id', ''):
                # Variant under current product
                if current_product and line['__parentId'] == current_product['id']:
                    variant = line.copy()
                    variant['inventory_levels'] = []
                    current_product['variants'].append(variant)
                    current_variant = variant
            elif 'InventoryLevel' in line.get('id', ''):
                # Inventory under current variant
                if current_variant and line['__parentId'] == current_variant['id']:
                    current_variant['inventory_levels'].append(line)
            elif 'src' in line:
                # Image under current product
                if current_product and line['__parentId'] == current_product['id']:
                    current_product['images'].append(line['src'])
        # Append the last product
        if current_product:
            self.products.append(current_product)
    
    def update_or_create_main_product(self):
        acum_percent = 90/len(self.products)
        progress = 10
        try:
            for index, product in enumerate(self.products):
                progress += acum_percent
                update_status_bot(self.item, progress = progress, status = f'Actualizando base: {index+1}/{len(self.products)}' )
                for i in [ i for i in product['variants'] if 'ProductVariant' in i.get('id')]: 
                    index += 1
                    try:
                        element, _ = MainProducts.objects.get_or_create(id_product = product['id'], id_variantShopi = i['id'])
                        element.sku = str(i['sku']).strip().upper()
                        element.save()
                    except Exception as error:
                            flag = True
                            while flag:
                                try: #TODO revisar si es necesario la verificación de los skus
                                    if 'duplicate key value violates unique constraint' in str(error): 
                                        element, _ = MainProducts.objects.get_or_create(id_product = product['id'], id_variantShopi = i['id'], sku = f" DUPLICADO - {i['sku']} - {index}" )
                                        print(product['id'])
                                        print(i['id'])
                                        print(i['sku'])
                                        print(error)
                                        flag=False
                                    if 'duplicate key value violates unique constraint' in str(error):
                                        print(error)
                                        index += 1
                                except Exception as e:
                                    index += 1
                                    print(e)
                    try:
                        element.title = product['title']
                        element.packaging_cost = (2765 + ((element.items_number-1)*623))
                        element.image_link = product['images'][0] if product['images'] else 'sin imagen'
                        element.stock = next((il['quantities'][0]['quantity'] for il in i['inventory_levels'] if il['location']['name'] == 'Bodega Envia'), 0)
                    except Exception as e:
                        if  ("list index out of range" in str(e)) & (product['status']!='ACTIVE'):
                            element.stock = 0
                    element.save()
                    item, _  = SopifyProducts.objects.get_or_create(MainProducts = element)
                    item.tags = product['tags']
                    item.vendor = product['vendor']
                    item.status = product['status']
                    item.compare_at_price = i['compareAtPrice']
                    item.barcode = i['barcode']
                    item.category = product['category'] or {}.get('fullName', 'Sin Categoria') 
                    item.save()
            update_status_bot(self.item, progress = 100, status = f'Proceso finalizado {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            handle_init_process(self.item, False)
        except Exception as e:
            raise(e)

    def update_products(self):
        self.get_all_products()
        self.update_or_create_main_product()