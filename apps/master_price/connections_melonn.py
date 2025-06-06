import requests
import re
import json
from decouple import config
from apps.master_price.models import MainProducts, melonn
import pandas as pd


class connMelonn:

    def __init__(self):
        self.headers = {
        'accept': 'application/json',
        'X-Api-Key': config('MELONN_API_KEY'),
        'Content-Type': 'application/json'
        }

    def create_data(self, data):
        data_order = {
            "orderNumber": ''.join(re.findall(r'\d+', data['note'])),
            "orderId": ''.join(re.findall(r'\d+', data['note'])),
            "comments": "SODIMAC",
            "requestProcessing": True,
            "holdFulfillmentAfterProcessing": False,
            "shipping": {
                "fullName": data['customer']['default_address']['name'],
                "addressL1": data['customer']['default_address']['address1'],
                "addressL2": data['customer']['default_address']['address2'],
                "city": 'BOGOTÁ, D.C.',
                "region": 'BOGOTÁ, D.C.',
                "country": 'Colombia',
                "postalCode": "00000",
                "phoneNumber": data['customer']['default_address']['phone']
            },
            "buyer": {
                "fullName": data['customer']['default_address']['name'],
                "phoneNumber": data['customer']['default_address']['phone'],
                "email": data['customer']['email']
            }
        }

        line_items = []

        for i in data['line_items']:
            dic = {}
            dic['sku'] = i['sku']
            dic['quantity'] = i['quantity']
            line_items.append(dic)

        data_order["lineItems"] = line_items
        data_order["shippingMethodTitle"] = "Envio Sodimac"
        self.data_order = data_order
    
    def create_order(self):
        response = requests.request("POST", config('MELONN_URL'), headers=self.headers, data= json.dumps(self.data_order))
        return response.json()
    
    def get_inventory(self):
        response= True
        products = []
        i = 1
        while response:
            url = config('MELONN_STOCK').format(page=i)
            i +=1
            response = requests.request("GET", url, headers=self.headers, data={}).json()
            products.extend(response)
        return products
    
    def set_inventory(self):
        con_m = connMelonn()
        products_melonn = con_m.get_inventory()
        products_missing = []
        for i in products_melonn:
            products = MainProducts.objects.filter(sku = i['sku'].upper())
            item = melonn.objects.get_or_create(publication = i['internalCode'])[0]
            if products:
                item.main_product = products[0]
            else:
                products_missing.append(i['sku'])
            item.sku = i['sku']
            item.publication = i['internalCode']
            item.stock = i['inventoryByWarehouse'][0]['availableQuantity']
            item.save() 
        df = pd.DataFrame(products_missing, columns=['sku'])
        df.to_excel('faltante shopify.xlsx', index=False)

