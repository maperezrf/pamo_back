from rest_framework.views import APIView
from apps.master_price.models import *
from rest_framework.response import Response
from rest_framework import status 
from apps.master_price.core import *
from pamo_back.constants import COLUMNS_ALL_PRODUCTS, COLUMNS_COUNT_RELATIONS
from apps.master_price.models import OAuthToken
from apps.master_price.connection_meli import connMeli
from apps.master_price.models import ProductsMeli, MainProducts
from apps.master_price.connections_google_sheets import ConnectionsGoogleSheets
import json
from unidecode import unidecode
from apps.master_price.handle_database import update_or_create_main_product, delete_main_product

class masterPriceAPIView(APIView):

    def get(self, request):
        query = read_sql('get_all_products')
        results = execute_query(query, COLUMNS_ALL_PRODUCTS )
        return Response( data = results, status=status.HTTP_200_OK)

class OAuthAPIView(APIView):  

    def get(self, request):
        self.update_products()
        return Response(data = {'price_cost'})
 
    def update_products(self):
        con_meli = connMeli()    
        price_cost = con_meli.get_taxes(20000)
        products = con_meli.get_all_publications()
        products_not_found = []
        for i in products:
            try:
                publicacion = con_meli.get_publication_detail(i)
                if publicacion['status'] == 'active':
                    item, create = ProductsMeli.objects.get_or_create(publication= i)
                    item.sku = unidecode([i for i in publicacion['attributes'] if i['id'] =='SELLER_SKU' ][0]['value_name'].upper().strip()) if len([ i for i in publicacion['attributes'] if i['id'] =='SELLER_SKU' ]) > 0 else ''
                    item_main, create = MainProducts.objects.get_or_create(sku=item.sku) if item.sku else (0, True)
                    if not create:
                        item.main_product =  item_main
                    item.pricePublication = publicacion['price']
                    item.crossed_out_price = publicacion['original_price']
                    item.free_shipping = publicacion['shipping']['free_shipping']
                    item.link = publicacion['permalink']
                    item.local_pick_up = publicacion['shipping']['local_pick_up']
                    item.store_pick_up = publicacion['shipping']['store_pick_up']
                    item.logistic_type = publicacion['shipping']['logistic_type']
                    item.weight = json.dumps([i for i in publicacion['attributes'] if (i['id'] == 'WEIGHT') | (i['id'] == 'PACKAGE_WEIGHT')])
                    item.save()
            except Exception as e:
                products_not_found.append(publicacion)
                print(e)
                print(publicacion)
        return Response(data = price_cost)

    def post(self, request):
        data = request.data
        pass


class NotificationHandlerShopífy(APIView):
    
    def post(self, request):
        print('\n**********************se recivió una notificación shopify******************************\n')
        data = request.data
        print(data)
        update_or_create_main_product(data)
        return Response(data = data)
    
class NotificationDeleteShopífy(APIView):
    
    def post(self, request):
        print('\n**********************se recivió una notificación shopify******************************\n')
        data = request.data
        print(data)
        delete_main_product(data)
        return Response(data = data)
    
class NotificationHandlerMeli(APIView):

    def post(self, request):
        print('\n**********************se recivió una notificación meli******************************\n')
        data = request.data
        print(data)
        return Response(data = data)

class ConnectionSheets(APIView):

    def get(self, request, process):
        if process == 'files':
            data = self.get_all_files()
        elif process == 'read_file':
            pass
        return Response( data, status=status.HTTP_200_OK)
        
    def post(self, request):
        id = request.data['id']
        conn = ConnectionsGoogleSheets()
        file = conn.read_file(id)
        sheets = conn.get_all_sheets(file)
        df = conn.sheet_to_df(file)
        df = df[[i for i in df.columns if i != '']]
        df = df.loc[(df['sku'] != '')].reset_index(drop=True)
        table = df.to_dict(orient='records')
        title = file.title
        data = {'table': table, 'title': title, 'columns':df.columns, 'sheets':sheets}
        return Response( data = data, status=status.HTTP_200_OK)
    
    def get_all_files(self):
        conn = ConnectionsGoogleSheets()
        files = json.dumps([{'title':i.title, 'id':i.id, 'url':i.url, 'last_update_time':i.lastUpdateTime } for i in conn.get_list_file()])
        return files
        