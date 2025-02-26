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
    utility = models.FloatField(null=True, blank=True, default=0)
    items_number = models.IntegerField(default=0, null=False, blank=False)
    commission_seller = models.FloatField(null=True, blank=True, default=0)
    publicity = models.FloatField(null=True, blank=True, default=0)
    aditional = models.FloatField(null=True, blank=True, default=0)
    packaging_cost = models.IntegerField(null=True, blank=True, default=0)
    image_link = models.CharField(max_length=500, null=True, blank=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    stock = models.IntegerField(default=0, null=False, blank=False)

class SopifyProducts(models.Model):
    MainProducts = models.ForeignKey(MainProducts, verbose_name = 'main_product', on_delete=models.CASCADE, null=True, blank=True)
    tags = models.CharField(max_length=500, null=True, blank=True)
    vendor = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    compare_at_price =models.FloatField(null=True, blank=True, default=0)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    cursor = models.CharField(max_length=80, null=True, blank=True)
    margen_comparacion_db = models.FloatField(null=True, blank=True, default=0)
    commission_platform = models.FloatField(null=True, blank=True, default=0)
    category = models.CharField(max_length=500, null=True, blank=True)


    def __str__(self) -> str:
        return self.sku if self.sku else ''
    
class ProductsSodimac(models.Model):
    main_product = models.ForeignKey(MainProducts, verbose_name = 'main_product', on_delete=models.CASCADE, null=True, blank=True)
    publication = models.CharField(max_length=50, null=True, blank=True, unique=True)
    ean = models.CharField(max_length=15, null=True, blank=True, unique=True)
    stock = models.IntegerField(null=True, blank=True ,default= 0)
    commission = models.SmallIntegerField(default = 0)
    shipment_cost = models.FloatField(null=True, blank=True, default=0)
    
class ProductsMeli(models.Model):
    main_product = models.ForeignKey(MainProducts, verbose_name = 'main_product', on_delete=models.CASCADE, null=True, blank=True)
    publication = models.CharField(max_length=50, null=True, blank=True, unique=True)
    commission = models.SmallIntegerField(default = 0)
    pricePublication = models.FloatField(null=True, blank=True, default=0)    
    crossed_out_price = models.FloatField(null=True, blank=True, default=0)    
    shipment_cost = models.FloatField(null=True, blank=True, default=0)
    link = models.CharField(max_length=300, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)

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
        
class melonn(models.Model):
    main_product = models.ForeignKey(MainProducts, verbose_name = 'main_product', on_delete=models.CASCADE, null=True, blank=True)
    publication = models.CharField(max_length=50, null=True, blank=True, unique=True)
    stock = models.IntegerField(default=0, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True, unique=True)