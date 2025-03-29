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
        dic = {}
        for _, line in enumerate(json_lines):
            if 'tags' in line:
                if dic:
                    dic = {}
                    self.products.append(dic)
                dic['product_id'] = line
                dic['variant'] = []
            elif '__parentId' in line:
                if 'id' in line:
                    dic['variant'].append(line)
                if 'src' in line:
                    dic['image'] = line
    
    def update_or_create_main_product(self):
        acum_percent = 90/len(self.products)
        progress = 10
        try:
            for index, product in enumerate(self.products):
                progress += acum_percent
                update_status_bot(self.item, progress = progress, status = f'Actualizando base: {index+1}/{len(self.products)}' )
                for i in product['variant']: 
                    index += 1
                    try:
                        element, _ = MainProducts.objects.get_or_create(id_product = product['product_id']['id'], id_variantShopi = i['id'])
                        element.sku = str(i['sku']).strip().upper()
                        element.save()
                    except Exception as error:
                            flag = True
                            while flag:
                                try: #TODO revisar si es necesario la verificación de los skus
                                    if 'duplicate key value violates unique constraint' in str(error): 
                                        element, _ = MainProducts.objects.get_or_create(id_product = product['product_id']['id'], id_variantShopi = i['id'], sku = f" DUPLICADO - {i['sku']} - {index}" )
                                        print(product['product_id']['id'])
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
                    element.title = product['product_id']['title']
                    element.packaging_cost = (2765 + ((element.items_number-1)*623))
                    element.image_link = product['image']['src'] if 'image' in product else 'sin imagen'
                    element.stock = i['inventoryQuantity']
                    element.save()
                    item, _  = SopifyProducts.objects.get_or_create(MainProducts = element)
                    item.tags = product['product_id']['tags']
                    item.vendor = product['product_id']['vendor']
                    item.status = product['product_id']['status']
                    item.compare_at_price = i['compareAtPrice']
                    item.barcode = i['barcode']
                    item.category = product['product_id']['category']['fullName'] if product['product_id']['category'] else 'Sin Categoria'
                    item.save()
            update_status_bot(self.item, progress = 100, status = f'Proceso finalizado {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            handle_init_process(self.item, False)
        except Exception as e:
            raise(e)

    def update_products(self):
        self.get_all_products()
        self.update_or_create_main_product()