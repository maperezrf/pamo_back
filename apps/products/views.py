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
from apps.master_price.handle_database import update_or_create_main_product 
from apps.master_price.connections_melonn import connMelonn
from apps.master_price.connections_melonn import connMelonn

def update(request):
    print(f'*** inicia actualizacion base productos {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}***')
    try:
        shopi = ConnectionsShopify()
        products = shopi.get_all_products()
        update_or_create_main_product(products)
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
    con_melonn = connMelonn()
    products = con_melonn.get_inventory()
    try:
        ProductsSodimac.objects.all().delete()
        data = {'status': 'success'}
        df = pd.read_excel('C:/Users/maper/Downloads/SKU SODIMAC 150225.xlsx')
        listado_not_found = []
        listado = []
        cont = 0
        for index, row in df.iterrows():
            try:
                item = ProductsSodimac()
                item.main_product = MainProducts.objects.filter(sku = str(row['SKU PAMO']).strip().upper()).first()
                item.publication = row.ID_PRODUCTO
                item.ean = row.EAN
                item.save()
                if not item.main_product:
                    listado_not_found.append(row['SKU PAMO'])
                    print(row['SKU PAMO'])
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
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
        products_sodi = ProductsSodimac.objects.filter(main_product__isnull=False)
        ids = [i.main_product.id_variantShopi for i in products_sodi]
        products_sodi = products_sodi.values()
        main_products = MainProducts.objects.filter(id_variantShopi__in = ids).values()
        products_sodi_df = pd.DataFrame(products_sodi)
        main_products_df = pd.DataFrame(main_products)
        merge = products_sodi_df.merge(main_products_df[['stock', 'id_variantShopi','sku']], how='left', left_on= 'main_product_id', right_on= 'id_variantShopi', suffixes=('_sodi', '_main'))
        data = merge.loc[merge['stock_main'].notna()][['ean','stock_main']].rename(columns={'stock_main':'inventarioDispo'}).to_dict(orient="records")
        con = ConnectionsSodimac()
        con.set_inventory(data)
        data = {'status': 'success'}
    except Exception as e:
        print(e)
        data = {'status': 'fail'}
    print(data)
    print(f'*** Finaliza seteo stock sodimac {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}***')
    return JsonResponse (data)