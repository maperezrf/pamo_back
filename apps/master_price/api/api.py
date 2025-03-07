from rest_framework.views import APIView
import json
from unidecode import unidecode
from django.http import JsonResponse
from apps.master_price.models import *
from rest_framework.response import Response
from rest_framework import status 
from apps.master_price.core import *
from pamo_back.constants import COLUMNS_SHOPIFY
from apps.master_price.connection_meli import connMeli
from apps.master_price.connections_google_sheets import ConnectionsGoogleSheets
from apps.master_price.conecctions_shopify import ConnectionsShopify
from apps.master_price.connection_meli import connMeli
from apps.master_price.connections_melonn import connMelonn
from apps.master_price.handle_database import update_or_create_main_product, delete_main_product
from pamo_back.queries import *
from apps.master_price.utils import read_seets


class masterPriceAPIView(APIView):

    def get(self, request):
        query = read_sql('get_shopify_products')
        results = execute_query(query, COLUMNS_SHOPIFY )
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
                if (publicacion['status'] == 'active') | (publicacion['status'] == 'paused'):
                    item, create = ProductsMeli.objects.get_or_create(publication= i)
                    item.sku = unidecode([i for i in publicacion['attributes'] if i['id'] =='SELLER_SKU' ][0]['value_name'].upper().strip()) if len([ i for i in publicacion['attributes'] if i['id'] =='SELLER_SKU' ]) > 0 else ''
                    item_main =  MainProducts.objects.filter(sku=item.sku.strip().upper())
                    if item_main:
                        item.main_product =  item_main[0]
                    else:
                        print(item.sku.strip().upper())
                    item.commission = 18
                    item.pricePublication = publicacion['price']
                    item.crossed_out_price = publicacion['original_price']
                    item.link = publicacion['permalink']
                    # TODO pendiente el precio base
                    # price_whitout_shipped = (item_main.price_base/(100- item.commission)*100)
                    # if (price_whitout_shipped < 3000):
                    #     commission_aditional = 2500
                    # elif (price_whitout_shipped >= 30000) & (price_whitout_shipped <= 60000) :
                    #     commission_aditional = 4000
                    # else:
                    #     commission_aditional = 0
                    # price_comissions = price_whitout_shipped + commission_aditional
                    # item.shipment_cost if price_comissions < 60000 else 0
                    # item.projected_price = round(price_comissions + item.shipment_cost)
                    item.status = publicacion['status']
                    item.save()
                else:
                    print(publicacion)
            except Exception as e:
                products_not_found.append(publicacion)
                print(e)
                print(publicacion)
        return Response(data = price_cost)

    def post(self, request):
        data = request.data
        pass


class NotificationProductShopy(APIView):
    
    def post(self, request):
        print('\n**********************se creo o actualizo un producto una notificación shopify******************************\n')
        dic = request.data
        dic_data ={
        'product_id': {'id': dic['admin_graphql_api_id'],
        'tags' : dic['tags'].split(','),
        'title': dic['title'],
        'vendor': dic['vendor'],
        'status': dic['status'],
        'category': {'fullName': 'Uncategorized'}},
        'variant': [{
            'id': i['admin_graphql_api_id'],
            'price': i['price'],
            'compareAtPrice':  i['compare_at_price'] if i['compare_at_price'] else 0,
            'sku': i['sku'],
            'barcode': i['barcode'],
            'inventoryQuantity': i['inventory_quantity'],
            'image': None,
            'inventoryItem': {'unitCost': {'amount': '45100.0'}}, #TODO hay que crear una consulta para traer el costo por que no se tiene
            '__parentId': dic['admin_graphql_api_id']
        } for i in dic['variants']]}
        update_or_create_main_product([dic_data])
        return Response(data = dic_data)

class NotificationCreateOrderShopify(APIView):
        
        def post(self, request):
            print('\n********************** Orden creada shopify ******************************\n')
            data = request.data
            print(data)
            if data['customer']['first_name'] == 'SODIMAC COLOMBIA S A':
                con = connMelonn()
                con.create_data(data)
                response = con.create_order()
                print(response)
                if response['statusCode'] == 201:
                    return  JsonResponse( data = {'message':'success'}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse( data = {'message':response['message']}, status=response['statusCode'])

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
        df, file, sheets_dic = read_seets(id)
        table = df.to_dict(orient='records')
        title = file.title
        data = {'table': table, 'title': title, 'columns':df.columns, 'sheets':sheets_dic}
        return Response( data = data, status=status.HTTP_200_OK)
    
    def get_all_files(self):
        conn = ConnectionsGoogleSheets()
        files = json.dumps([{'title':i.title, 'id':i.id, 'url':i.url, 'last_update_time':i.lastUpdateTime } for i in conn.get_list_file()])
        return files
        

class ConnectionShopify(APIView):

    def get(self, request):

        return Response( status=status.HTTP_200_OK)

    def post(self, request):
        id = request.data['id']
        self.send_data_shopify(id)
    
    def send_data_shopify(self, id):
        # TODO Se debe agregar el inventoryLevelId a la base de datos para actualizar los stocks
        # TODO agregar metodo para identificar columnas sin datos y quitarlas
        df, file, sheets_dic = read_seets(id)
        # file = pd.read_excel('C:/Users/USUARIO/Downloads/CATALOGO IMPORTADORA BARU SAS 2009.xlsx')
        df.rename(columns={'titulo':'title', 'costo':'cost', 'stock':'inventory_quantity', 'proveedor':'vendor', 'estado':'status', 'categoria':'category', 'codigo de barras':'barcode'}, inplace=True)
        columns = [i for i in df.columns if i in ['sku','title','cost','inventory_quantity','vendor','status','category','barcode']]
        novelty_list=[]
        list_items=[]
        for index, row in df.iterrows():
            try:
                item = SopifyProducts.objects.get(MainProducts__sku = row['sku'])
                if 'title' in columns:
                    item.MainProducts.title = row.title
                if 'cost' in columns:
                    item.MainProducts.cost = round(int(row.cost))
                if 'inventory_quantity' in columns:
                    item.MainProducts.inventory_quantity = row.inventory_quantity
                if 'tags' in columns:
                    item.tags = row.tags
                if 'vendor' in columns:
                    item.vendor = row.provevendoredor
                if 'status' in columns:
                    item.status = row.status
                if 'category' in columns:
                    item.category = row.category
                if 'barcode' in columns:
                    item.barcode = row.barcode
                item.MainProducts.save()
                item.save()
                list_items.append(row['sku'])
            except Exception as e:
                if 'SopifyProducts matching query does not exist' in str(e):
                    dic_novelty = {}
                    dic_novelty['sku'] = row.sku
                    dic_novelty['novedad'] = 'sku no encontrado'
                    novelty_list.append(dic_novelty)
                else:
                    raise e
        pd.DataFrame(novelty_list).to_excel('C:/Users/USUARIO/Desktop/pamo/pamo_back/apps/master_price/media/novedades.xlsx', index=False)
        main_products = MainProducts.objects.filter(sku__in = list_items)
        main_products_df = pd.DataFrame(main_products.values())
        items = SopifyProducts.objects.filter(MainProducts__sku__in = list_items)
        df_items_df = pd.DataFrame(items.values())
        merge = main_products_df.merge(df_items_df, how='left',right_on='MainProducts_id', left_on='id_variantShopi' )
        columns = list(columns)
        columns.extend(['id_variantShopi', 'id_product', 'projected_price', 'projected_compare_at_price'])
        self.set_variables( merge[columns])
        return merge[columns]
    


    def set_variables(self, df):
        print('seteando variables')
        variables = []
        columns = df.columns
        for index, row in df.iterrows():
            variants = {'id':row.id_variantShopi}
            # variants['sku'] = row.sku
            product = {'id':row.id_product}
            # inventory = {'inventoryLevelId':self.df_rev.loc[i]['inventorylevelsid']}
            if 'title' in columns:
                product['title'] = row.title
            if 'vendor' in columns:
                product['vendor'] = row.vendor
            if 'status' in columns:
                product['status'] = 'ACTIVE' if str(row.status) == '1' else 'DRAFT'
            if 'tags' in columns:
                tags_archive= row.tags.strip(',').split(',')
                tags_shopi = row.tags_shopi
                tags_new = [i.upper() for i in [i.lower().strip() for i in tags_archive] if i not in [j.lower().strip() for j in tags_shopi ]]
                tags_shopi.extend(tags_new)
                product['tags'] = tags_shopi
                if 'PAUSADO' in product['tags']:
                    variants['inventoryPolicy'] = 'DENY'
            if 'barcode' in columns:
                variants['barcode'] = row.barcode
            if 'projected_compare_at_price' in columns:
                variants['compareAtPrice'] = row.projected_compare_at_price
            if 'projected_price' in columns:
                variants['price'] = row.projected_price
            if 'cost' in columns:
                variants["inventoryItem"]={'cost':str(row.cost)}
            # try:
            #     inventory["availableDelta"] = int(self.df_rev.loc[i]['stock']) - int(self.df_rev.loc[i]['inventoryquantity_shopi'])
            # except:
            #     pass

            var ={}
            if any([True for i in ['title','vendor','status','tags'] if i in product]):
                var['productInput'] = product
            if any([True for i in ['sku','barcode','compareAtPrice','price','inventoryItem'] if i in variants ]):
                var['variantInput'] = variants
            # if 'availableDelta' in inventory:
            #     var['inventoryAdjustInput'] = inventory
            variables.append(var)

        # TODO refactorizar de aqui, se hace el envio a Shopify
        shopi = ConnectionsShopify()
        for index, variable in enumerate(variables):
            print(len(variables)-index)
            product_var = product_hql = variant_var = variant_hql = inventory_var = inventory_hql = ''
            if "productInput" in variable :
                product_var = "$productInput: ProductInput!,"
                product_hql = UPTADE_PRODUCT
            if "variantInput" in variable:
                variant_var = '$variantInput: ProductVariantInput!,'
                variant_hql = PRODUCT_VARIANT_UPDATE
            if "inventoryAdjustInput" in variable:
                inventory_var = '$inventoryAdjustInput: InventoryAdjustQuantityInput!,'
                inventory_hql = INVENTORY_ADJUST
            query = UPDATE_QUERY.format(productInput = product_var, variantInput = variant_var, inventoryAdjustInput = inventory_var, productUpdateq = product_hql, productVariantUpdateq = variant_hql, inventoryAdjustQuantity = inventory_hql)
            res = shopi.request_graphql(query, variable)
            if 'errors' in  [i for i in res.json()]:
                print(f'error {row.sku}' )
            else:
                print('ok')
        return variables