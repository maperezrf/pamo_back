import requests
import re
import json
from decouple import config


class connMelonn:

    def __init__(self):
        self.url = config('MELONN_URL')
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
                "addressL1": "Av. Kentucky 1234",
                "addressL2": "optional to complete the address",
                "city": data['customer']['default_address']['city'],
                "region": data['customer']['default_address']['city'],
                "country": data['customer']['default_address']['country'],
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
        response = requests.request("POST", self.url, headers=self.headers, data= json.dumps(self.data_order))
        return response.json()