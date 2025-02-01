import requests
import urllib.parse
from hashlib import sha256
from hmac import HMAC
from datetime import datetime
from pamo_back.constants import *

class ConnectionFalabella():

    def __init__(self):
        self.url = FALABELLA_URL
        self.api_key = FALABELLA_API_KEY

        self.headers = {
        'Accept': 'application/xml',
        'Content-Type': 'application/xml',
        }
    
    def generate_signature(self, api_key, parameters):
        """
        Generates an HMAC-SHA256 signature for API requests.

        Args:
            api_key (str): Your API key provided by the service.
            parameters (dict): A dictionary containing request parameters.

        Returns:
            str: The generated signature in hexadecimal format.
        """
        sorted_params = sorted(parameters.items())
        concatenated = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
        signature = HMAC(api_key.encode('utf-8'), concatenated.encode('utf-8'), sha256).hexdigest()
        return signature

    def request_falabella(self, process, payload=[]):
        parameters = {
            'UserID': 'gerencia@pamo.co',
            'Version': '1.0',
            'Action': process,
            'Format': 'JSON',
            'Timestamp': datetime.now().isoformat()
        }
        parameters['Signature'] = self.generate_signature(self.api_key, parameters.copy())
        response = requests.post(self.url, headers=self.headers, params=parameters, data=payload)
        return response