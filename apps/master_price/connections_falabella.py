import requests
import xml.etree.ElementTree as ET
import urllib.parse
from hashlib import sha256
from hmac import HMAC
from datetime import datetime
from pamo_back.constants import URL_API_FALABELLA, API_KEY_FALABELLA, USER_ID_FALABELLA
from apps.master_price.models import StatusProcess, ProductsFala, MainProducts
from apps.master_price.utils import create_product, handle_init_process, update_status_bot
import pandas as pd


class ConnectionFalabella():

    def __init__(self):
        self.url = URL_API_FALABELLA
        self.api_key = API_KEY_FALABELLA

        self.headers = {
        'Accept': 'application/xml',
        'Content-Type': 'application/xml',
        }
    
    def generate_signature(self, parameters):
        """
            Genera una firma HMAC-SHA256 para solicitudes de API.

            Argumentos:

            api_key (str): Tu clave de API proporcionada por el servicio.
            parameters (dict): Un diccionario que contiene los parámetros de la solicitud.
            Devuelve:

            str: La firma generada en formato hexadecimal.
        """
        sorted_params = sorted(parameters.items())
        concatenated = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
        signature = HMAC(self.api_key.encode('utf-8'), concatenated.encode('utf-8'), sha256).hexdigest()
        return signature

    def request_falabella(self, process, payload=[]):

        parameters = {
            'UserID': USER_ID_FALABELLA,
            'Version': '1.0',
            'Action': process,
            'Format': 'JSON',
            'Timestamp': datetime.now().isoformat()
        }

        parameters['Signature'] = self.generate_signature(parameters.copy())
        response = requests.post(self.url, headers=self.headers, params=parameters, data=payload)
        return response.json()['SuccessResponse']['Body']['Products']['Product'] if process == 'GetProducts' else response

    def get_products_detail(self, publications):
        add_base_products = []
        for publication in publications:
            detail = {}
            detail['sku'] = publication['SellerSku']
            detail['publication'] = publication['ShopSku']
            stock = publication['BusinessUnits']['BusinessUnit']['Stock']
            detail['stock'] = int(stock) if stock else 0
            detail['url_publication'] = publication['Url']
            detail['status'] = publication['BusinessUnits']['BusinessUnit']['Status']
            detail['Price'] = float(publication['BusinessUnits']['BusinessUnit']['Price'])
            add_base_products.append(detail)
        return add_base_products


    def build_request(sefl):
        """
        Construye un XML con múltiples productos.

        Args:
            products (list): Lista de productos, donde cada producto es un diccionario con sus datos.

        Returns:
            str: Cadena XML generada.
        """
        products = ProductsFala.objects.all()
        root = ET.Element("Request")
        for product_fala in  products:
            main_product = product_fala.main_product
            if main_product:
                product = ET.SubElement(root, "Product")
                seller_sku = ET.SubElement(product, "SellerSku")
                seller_sku.text = main_product.sku
                business_units = ET.SubElement(product, "BusinessUnits")
                business_unit = ET.SubElement(business_units, "BusinessUnit")
                operator_code = ET.SubElement(business_unit, "OperatorCode")
                operator_code.text = 'faco'
                stock = ET.SubElement(business_unit, "Stock")
                stock.text = str(main_product.stock)
        xml_string = ET.tostring(root, encoding="unicode", method="xml")
        return xml_string
    
    def get_products_to_add(self):
        try:
            self.item, _ = StatusProcess.objects.get_or_create(name='fala_update')
            handle_init_process(self.item, True)
            update_status_bot(self.item, 5, "Solicitando productos")
            products = self.request_falabella('GetProducts')
            update_status_bot(self.item, 20, "Codificando respuesta")
            products_to_add = self.get_products_detail(products)
            create_product(products_to_add, ProductsFala, self.item)
            update_status_bot(self.item, progress = 100, status = f'Proceso finalizado {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            handle_init_process(self.item, False)
        except Exception as e:
            update_status_bot(self.item, progress = 0, status = f'El proceso falló :{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            handle_init_process(self.item, False)
    
    def set_inventory(self):
        payload = self.build_request()
        return self.request_falabella('ProductUpdate', payload)