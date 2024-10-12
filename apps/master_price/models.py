from typing import Iterable
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import ast

class MainProducts(models.Model):
    id_variantShopi = models.CharField(max_length=300, null=False, blank=False, primary_key=True)
    id_product = models.CharField(max_length=300, null=False, blank=False) 
    sku = models.CharField(max_length=100, null=True, blank=True, unique=True)
    cost = models.FloatField(null=True, blank=True, default=0)
    utility = models.FloatField(null=True, blank=True, default=18)
    items_number = models.IntegerField(default=1, null=False, blank=False)
    commission_seller = models.FloatField(null=True, blank=True, default=2)
    publicity = models.FloatField(null=True, blank=True, default=2)
    aditional = models.FloatField(null=True, blank=True, default=0)
    packaging_cost = models.IntegerField(null=True, blank=True, default=0)
    price_base = models.IntegerField(null=True, blank=True, default=0)
    image_link = models.CharField(max_length=500, null=True, blank=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    inventory_quantity = models.IntegerField(null=True, blank=True ,default= 0)

    def save(self, *args, **kwargs) -> None:
        if self.utility == None:
            self.utility=18
        if self.items_number == None:
            self.items_number = 1
        if self.publicity == None:
            self.publicity = 2
        if self.commission_seller == None:
            self.commission_seller = 2
        if self.aditional == None:
            self.aditional = 0
        if self.cost != 0:
            utility = (float(self.cost) / (100-self.utility) * 100)
            cost_packagin = 2765+((self.items_number-1) * 623)
            self.price_base = round(((utility + cost_packagin)/(100-self.commission_seller)*100)/(100-self.publicity)*100) + self.aditional
        return super().save(*args, **kwargs)

class SopifyProducts(models.Model):
    MainProducts = models.ForeignKey(MainProducts, verbose_name = 'main_product', on_delete=models.CASCADE, null=True, blank=True)
    tags = models.CharField(max_length=500, null=True, blank=True)
    vendor = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    real_price = models.FloatField(null=True, blank=True, default=0)
    compare_at_price = models.FloatField(null=True, blank=True, default=0)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    margen_comparacion_db = models.FloatField(null=True, blank=True, default=0)
    commission_platform = models.FloatField(null=True, blank=True, default=0)
    category = models.CharField(max_length=500, null=True, blank=True)
    projected_price = models.FloatField(null=True, blank=True, default=0)
    projected_compare_at_price = models.FloatField(null=True, blank=True, default=0)
    shipment_cost = models.FloatField(null=True, blank=True, default=0)
    margen = models.FloatField(null=True, blank=True, default=0)

    def __str__(self) -> str:
        return self.sku if self.sku else ''
    
    def save(self, *args, **kwargs) -> None:
        if self.commission_platform == None:
            self.commission_platform = 18
        if self.margen_comparacion_db == None:
            self.margen_comparacion_db = 7
        if self.MainProducts.price_base != 0:
            price_whitout_shipment = (self.MainProducts.price_base/(100-self.commission_platform)*100)
            self.shipment_cost = 0 if price_whitout_shipment < 100000 else 7000
            self.projected_price = round(price_whitout_shipment + self.shipment_cost )
            self.projected_compare_at_price = round(self.projected_price / (self.margen_comparacion_db / 10))
        return super().save(*args, **kwargs) 
    
class ProductsSodimac(models.Model):
    MainProducts = models.ForeignKey(MainProducts, verbose_name = 'main_product', on_delete=models.CASCADE, null=True, blank=True)
    publication = models.CharField(max_length=50, null=True, blank=True, unique=True)
    ean = models.CharField(max_length=15, null=True, blank=True, unique=True)
    stock = models.IntegerField(null=True, blank=True ,default= 0)
    commission = models.SmallIntegerField(default = 0)
    guide = models.FloatField(null=True, blank=True, default=0)
    shipment_cost = models.FloatField(null=True, blank=True, default=0)
    pricePublication = models.FloatField(null=True, blank=True, default=0)    

    def save(self, *args, **kwargs ) -> None:
        if (self.guide == None) | (self.guide == 0):
            self.guide =  1500
        if (self.commission == None) | (self.commission == 0):
            self.commission = 2
        if (self.shipment_cost == None) | self.shipment_cost == 0:
            self.shipment_cost = 6900
        self.pricePublication = round(self.MainProducts.price_base/(100-self.commission)*100) + self.guide + self.shipment_cost
        return super().save(args, **kwargs)
    
class ProductsMeli(models.Model):
    MainProducts = models.ForeignKey(MainProducts, verbose_name = 'main_product', on_delete=models.CASCADE, null=True, blank=True)
    publication = models.CharField(max_length=50, null=True, blank=True, unique=True)
    commission = models.SmallIntegerField(default = 0)
    pricePublication = models.FloatField(null=True, blank=True, default=0)    
    crossed_out_price = models.FloatField(null=True, blank=True, default=0)    
    shipment_cost = models.FloatField(null=True, blank=True, default=0)
    link = models.CharField(max_length=300, null=True, blank=True)
    projected_price = models.FloatField(null=True, blank=True, default=0)

class OAuthToken(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key = self.get_encryption_key()
        self.cipher_suite = Fernet(key)

    def encrypt_token(self, token):
        if isinstance(token, str):
            return self.cipher_suite.encrypt(token.encode())
        else:
            raise TypeError("El token debe ser una cadena de texto")

    def decrypt_token(self, encrypted_token):
        if isinstance(encrypted_token, bytes):
            return self.cipher_suite.decrypt(encrypted_token).decode()
        else:
            raise TypeError("El token encriptado debe ser un objeto de tipo bytes")

    def save(self, *args, **kwargs):
        self.access_token = self.encrypt_token(self.access_token)
        self.refresh_token = self.encrypt_token(self.refresh_token)
        super().save(*args, **kwargs)

    def get_access_token(self):
        return self.decrypt_token(ast.literal_eval(self.access_token))

    def get_refresh_token(self):
        return self.decrypt_token(ast.literal_eval(self.refresh_token))

    def get_encryption_key(self):
        try:
            return settings.ENCRYPTION_KEY.encode()  # Esto debe ser bytes
        except AttributeError:
            raise ImproperlyConfigured("No se ha configurado la clave de encriptación")