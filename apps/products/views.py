from django.http import JsonResponse
from apps.master_price.models import *
from pamo_back.queries import *
from apps.master_price.conecctions_shopify import ConnectionsShopify
import time
from datetime import datetime
from unidecode import unidecode
import pandas as pd
from apps.master_price.connection_meli import connMeli
from apps.master_price.connections_sodimac import ConnectionsSodimac

def update(request):
    print(f'*** inicia actualizacion base productos {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}***')
    try:
        shopi = ConnectionsShopify()
        shopi.get_all_products()
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
        dic['MainProducts'] = MainProducts.objects.get(id_variantShopi = id)
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

    # con = ConnectionsSodimac()
    # con.set_inventory_all()
    
    try:
        data = {'status': 'success'}
        df = pd.read_csv('C:/Users/USUARIO/Downloads/SKU SODIMAC EAN (2).csv', sep=';')
        listado_not_found = []
        listado = []
        cont = 0
        for index, row in df.iterrows():
            try:
                item = ProductsSodimac()
                item.MainProducts = MainProducts.objects.get(sku = row.sku_pamo)
                item.publication = row.sku_sodimac
                item.ean = row.ean
                item.save()
            except Exception as e:
                if 'MainProducts matching query does not exist.' in str(e):
                    listado_not_found.append(row.sku_pamo)
                    print(row.sku_pamo)
                    print(e)
                elif 'UNIQUE constraint failed' in str(e):
                    print(e)
                else:
                    raise e 
    except Exception as e:
        print(e)
        data = {'status': 'fail'}
    return JsonResponse(data)

def set_all_inventory_sodimac(request):
    print(f'*** inicia seteo stock sodimac {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}***')
    try:
        products = ProductsSodimac.objects.all() 
        data = {i.ean: i.MainProducts.inventory_quantity for i in products}
        con = ConnectionsSodimac()
        con.set_inventory(data)
        data = {'status': 'success'}
    except Exception as e:
        print(e)
        data = {'status': 'fail'}
    print(data)
    print(f'*** Finaliza seteo stock sodimac {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}***')
    return JsonResponse (data)
    