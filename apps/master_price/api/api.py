from rest_framework.views import APIView
from apps.master_price.models import *
from rest_framework.response import Response
from rest_framework import status 
from apps.master_price.core import *
from pamo_back.constants import COLUMNS_ALL_PRODUCTS, COLUMNS_COUNT_RELATIONS
from apps.master_price.models import OAuthToken
from apps.master_price.connection_meli import connMeli
from apps.master_price.models import ProductsMeli, MainProducts
import json
from unidecode import unidecode

class masterPriceAPIView(APIView):

    def get(self, request):
        query = read_sql('get_all_products')
        results = execute_query(query, COLUMNS_ALL_PRODUCTS )
        return Response( data = results, status=status.HTTP_200_OK)

class OAuthAPIView(APIView):  

    def get(self, request):
        return Response(data = {'price_cost'})
 
    def update_prodcuts():
        con = connMeli()    
        price_cost = con.get_taxes(20000)
        products = con.get_all_publications()
        for i in products:
            try:
                publicacion = con.get_publication_detail(i)
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
        return Response(data = data)
    
class NotificationHandlerMeli(APIView):

    def post(self, request):
        print('\n**********************se recivió una notificación meli******************************\n')
        data = request.data
        print(data)
        return Response(data = data)
