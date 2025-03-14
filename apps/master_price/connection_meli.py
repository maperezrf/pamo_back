from pamo_back.constants import APP_ID, CLIENT_SECRET, URL_REDIRECT, URL_GET_TOKEN
import requests
from datetime import datetime, timedelta
from django.core.exceptions import ImproperlyConfigured
from apps.master_price.models import OAuthToken
from pamo_back.constants import USER_ID
from unidecode import unidecode
from apps.master_price.models import StatusProcess, ProductsMeli
from apps.master_price.utils import create_product, handle_init_process, update_status_bot

class connMeli():
    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded'
    }
    
    def __init__(self):
        self.oauth  = OAuthToken.objects.get(id=1)
        if self.oauth.expires_at.replace(tzinfo=None) <= datetime.now():
            self.refresh_token()

    def refresh_token(self):
        refresh_token =  "TG-67d388d674e0b50001c029bc-82071021" #self.oauth.get_refresh_token()    
        self.get_token(refresh_token)
        
    def get_token(self, code_refresh):
        try:
            print('Obteniendo token')
            payload = f'grant_type=refresh_token&client_id={APP_ID}&client_secret={CLIENT_SECRET}&refresh_token={code_refresh}'
            response = requests.request("POST", URL_GET_TOKEN, headers=self.headers, data=payload)
            token = response.json()
            self.oauth.access_token = token['access_token']
            self.oauth.refresh_token = token['refresh_token']
            self.oauth.expires_at = datetime.now() + timedelta(hours=5, minutes=30) 
            self.oauth.save()
            print('se obtuvo el token correctamente')
        except Exception as e:
          raise ImproperlyConfigured(f'Error al tratar de obtener token {e}')
    
    def get_taxes(self, price):
        additional_cost = 0
        if (price <= 30000) :
            additional_cost = 2500
        elif (price > 30000) & (price < 60000):
            additional_cost = 4000
        publication_cost = (price*.16) + additional_cost
        return publication_cost
    
    def get_acces_token(self):
        return self.oauth.get_access_token()
    
    def get_publication_detail(self, id_publicatión):
        url = f'https://api.mercadolibre.com/items/{id_publicatión}'
        payload = {}
        self.headers['Authorization'] =  f'Bearer {self.get_acces_token()}'
        response = requests.request("GET", url, headers=self.headers, data=payload)
        return response.json()

    def get_all_publications(self):
        acces_token = self.get_acces_token()
        try:
            publications = []
            cont = 0 
            while True:
                url = f"https://api.mercadolibre.com/users/{USER_ID}/items/search?access_token={acces_token}&limit=100&offset={cont}"
                response = requests.request("GET", url, headers={}, data={})
                cont += 100
                publications.extend(response.json()['results'])
        except Exception as e:
            print(e)
        return publications
    
    def get_publications_for_sku(self, sku):
        url = F"https://api.mercadolibre.com/users/{USER_ID}/items/search?seller_sku={sku}"
        self.headers['Authorization'] =  self.get_acces_token()
        response = requests.request("GET", url, headers=self.headers, data={})
        return response.json()['results']

    def get_products_detail(self, publications):
        add_base_products = []
        for publication in publications:
            detail = {}
            publication_detail = self.get_publication_detail(publication)
            atributes = publication_detail.get('attributes', None)
            attribute_sku = [i for i in publication_detail['attributes'] if i['id'] =='SELLER_SKU' ]
            if (atributes != None) & (len(attribute_sku) >0 ):
                detail['sku'] = unidecode(attribute_sku[0]['value_name']).upper().strip()
            else:
                detail['sku'] = None
            detail['publication'] = publication_detail['id']
            detail['stock'] = publication_detail['available_quantity']
            detail['commission'] = 18
            detail['url_publication'] = publication_detail['permalink']
            detail['status'] = publication_detail['status']
            detail['Price'] = publication_detail['price']
            add_base_products.append(detail)
        return add_base_products

    def get_products_to_add(self):
        try:
            self.item, _ = StatusProcess.objects.get_or_create(name='meli_update')
            handle_init_process(self.item, True)
            update_status_bot(self.item, 5, "Solicitando productos")
            products = self.get_all_publications()
            update_status_bot(self.item, 20, "Codificando respuesta")
            products_to_add = self.get_products_detail(products)
            create_product(products_to_add, ProductsMeli, self.item)
            update_status_bot(self.item, progress = 100, status = f'Proceso finalizado {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            handle_init_process(self.item, False)
        except Exception as e:
            update_status_bot(self.item, progress = 0, status = f'El proceso falló :{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            handle_init_process(self.item, False)
            