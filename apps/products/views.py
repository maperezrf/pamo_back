from django.http import JsonResponse
from apps.master_price.models import *
from pamo_back.queries import *
from apps.master_price.conecctions_shopify import ConnectionsShopify
import time
from datetime import datetime
from unidecode import unidecode
import pandas as pd
from apps.master_price.connection_meli import connMeli

def update(request):
    print(f'*** inicia actualizacion base productos {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}***')
    try:
        shopi = ConnectionsShopify()
        list_products = []
        response =shopi.request_graphql(GET_PRODUCTS.format(cursor=''))
        list_products.append(response.json()['data']['products']['edges'])
        cursor_new = response.json()['data']['products']['pageInfo']['endCursor']
        while response.json()['data']['products']['pageInfo']['hasNextPage']:
            time.sleep(20)
            response =shopi.request_graphql(GET_PRODUCTS.format(cursor= f",after:\"{response.json()['data']['products']['pageInfo']['endCursor']}\""))
            print(response.json()['extensions'])
            cursor_new = response.json()['data']['products']['pageInfo']['endCursor']
            list_products.append(response.json()['data']['products']['edges'])
            print(len(list_products))
        data_list = []
        try:
            for i in list_products:
                for k in i:
                    variants_cont = 1 
                    try:
                        while len(k['node']['variants']['edges']) >= variants_cont:
                                dic = {}
                                dic['id_product'] = k['node']['id'].replace('gid://shopify/Product/',"")
                                dic['tags'] = ', '.join(k['node']['tags']) if len(k['node']['tags']) > 0 else None
                                dic['title'] = k['node']['title']
                                dic['vendor'] = k['node']['vendor']
                                dic['status'] = k['node']['status']
                                dic['id_variantShopi'] = k['node']['variants']['edges'][variants_cont - 1]['node']['id'].replace('gid://shopify/ProductVariant/', '')
                                dic['price'] =float(k['node']['variants']['edges'][variants_cont - 1]['node']['price']) if k['node']['variants']['edges'][variants_cont - 1]['node']['price'] !=None else 0.0 
                                dic['compare_at_price'] =float(k['node']['variants']['edges'][variants_cont - 1]['node']['compareAtPrice']) if k['node']['variants']['edges'][variants_cont - 1]['node']['compareAtPrice'] !=None else 0.0 
                                dic['sku'] = unidecode(k['node']['variants']['edges'][variants_cont - 1]['node']['sku'].upper().strip()) if k['node']['variants']['edges'][variants_cont - 1]['node']['sku'] != None else k['node']['variants']['edges'][variants_cont - 1]['node']['sku']
                                dic['barcode'] = k['node']['variants']['edges'][variants_cont - 1]['node']['barcode']
                                dic['inventory_quantity'] = int(float(k['node']['variants']['edges'][variants_cont - 1]['node']['inventoryQuantity'])) if float(k['node']['variants']['edges'][variants_cont - 1]['node']['inventoryQuantity']) != None else 0.0
                                try:
                                    dic['image_link'] = k['node']['variants']['edges'][0]['node']['image'] if k['node']['variants']['edges'][0]['node']['image'] != None else k['node']['images']['nodes'][0]['src'] if k['node']['images']['nodes'][0]['src'] else ''
                                except Exception as e:
                                    dic['image_link'] = 'sin imagen'
                                    print(e)
                                variants_cont += 1
                                data_list.append(dic)
                    except Exception as e:
                        print(e)
                        print(k)
        except Exception as e:
            print(e)
            print(k)
        dic['cursor'] = cursor_new
        data_to_save = [MainProducts(**elemento) for elemento in data_list]
        MainProducts.objects.bulk_create(data_to_save)
        data = {'status': 'success'}
        print(f'*** inicia actualizacion base productos {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}***')
    except Exception as e:
        print(e)
        data = {'status': 'fail'}
        print(f'*** la actualizacion de productos fallo {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}***')
    return JsonResponse(data)

def delete(request):
    MainProducts.objects.all().delete()
    data = {'status': 'success'}
    return JsonResponse(data)

def charge_data_meli(request):
    """
        Cargar datos mercadolibre
    """
    df = pd.read_csv('C:/Users/USUARIO/Desktop/pamo/pamo_web/meli.csv')
    listado = []
    for i in range(df.shape[0]):
        dic = {}
        id = df.loc[i, 'main_product_id']
        dic['main_product'] = MainProducts.objects.get(id_variantShopi = id)
        dic['publication'] = df.loc[i, 'publication']
        dic['taxes'] = df.loc[i, 'taxes']
        dic['margen'] = df.loc[i, 'margen']
        dic['pricePublication'] = df.loc[i, 'pricePublication']
        listado.append(dic)
    try:
        data_to_save = [ProductsMeli(**elemento) for elemento in listado]
        ProductsMeli.objects.bulk_create(data_to_save)
        data = {'status': 'success'}
    except Exception as e:
        print(e)
        data = {'status': 'fail'}
    return JsonResponse(data)

def charge_data_sodi(request):
    """
        Cargar datos sodimac
    """
    df = pd.read_csv('C:/Users/USUARIO/Desktop/pamo/pamo_web/sodi.csv')
    listado = []
    for i in range(df.shape[0]):
        try:
            dic = {}
            id = df.loc[i, 'main_product']
            dic['main_product'] = MainProducts.objects.get(id_variantShopi = id)
            dic['publication'] = df.loc[i, 'publication']
            dic['ean'] = df.loc[i, 'ean']
            dic['stock'] = df.loc[i, 'stock']
            dic['stock_sodi'] = df.loc[i, 'stock_sodi']
            listado.append(dic)
        except Exception as e:
            print(e)
    try:
        data_to_save = [ProductsSodimac(**elemento) for elemento in listado]
        ProductsSodimac.objects.bulk_create(data_to_save)
        data = {'status': 'success'}
    except Exception as e:
        print(e)
        data = {'status': 'fail'}
    return JsonResponse(data)

def test():
    pass