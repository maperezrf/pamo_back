from rest_framework import serializers
from apps.master_price.models import MainProducts, SopifyProducts

class SopifyProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SopifyProducts
        fields = [
            'tags', 'vendor', 'status', 'real_price', 'compare_at_price',
            'barcode', 'cursor', 'margen_comparacion_db', 'commission_platform',
            'category', 'projected_price', 'projected_compare_at_price', 'shipment_cost'
        ]

class MainProductsSerializer(serializers.ModelSerializer):
    sopify_products = SopifyProductsSerializer(source='sopifyproducts_set', many=True)

    class Meta:
        model = MainProducts
        fields = [
            'id_variantShopi', 'id_product', 'sku', 'cost', 'utility', 'items_number',
            'commission_seller', 'publicity', 'aditional', 'packaging_cost', 'price_base',
            'image_link', 'title', 'inventory_quantity', 'sopify_products' 
        ]