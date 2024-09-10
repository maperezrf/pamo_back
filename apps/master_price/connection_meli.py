from pamo_back.constants import APP_ID, CLIENT_SECRET, URL_REDIRECT, URL_GET_TOKEN
import requests
from datetime import datetime, timedelta
from django.core.exceptions import ImproperlyConfigured
from apps.master_price.models import OAuthToken
from pamo_back.constants import USER_ID


class connMeli():
    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded'
    }
    
    def __init__(self):
        self.item  = OAuthToken.objects.get(id=1)
        if self.item.expires_at.replace(tzinfo=None) <= datetime.now():
            self.refresh_token()

    def refresh_token(self):
        refresh_token = self.item.get_refresh_token()    
        self.get_token(refresh_token)
        
    def get_token(self, code_refresh):
        try:
            print('Obteniendo token')
            payload = f'grant_type=refresh_token&client_id={APP_ID}&client_secret={CLIENT_SECRET}&refresh_token={code_refresh}'
            response = requests.request("POST", URL_GET_TOKEN, headers=self.headers, data=payload)
            token = response.json()
            self.item.access_token = token['access_token']
            self.item.refresh_token = token['refresh_token']
            self.item.expires_at = datetime.now() + timedelta(hours=5, minutes=30) 
            self.item.save()
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
        return self.item.get_access_token()
    
    def get_publication_detail(self, id_publicatión):
        url = f'https://api.mercadolibre.com/items/{id_publicatión}'
        payload = {}
        self.headers['Authorization'] =  self.get_acces_token()
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
