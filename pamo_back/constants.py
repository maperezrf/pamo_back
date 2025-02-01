from decouple import config

# SHOPIFY
ACCES_TOKEN = config("ACCES_TOKEN") 
URL_GRAPHQL = config("URL_GRAPHQL") 
URL_REST = config("URL_REST")
SECRET_KEY_DJANGO = config("SECRET_KEY")
DEBUG_VAR = config('DEBUG', cast=bool)
URL_CREATE_ORDERS = config('URL_CREATE_ORDERS')

# SODIMAC
SUBSCRIPTION_KEY = config('SUBSCRIPTION_KEY') 
REFERENCIA_FPRN = config('REFERENCIA_FPRN')
ID_SODIMAC = config('ID_SODIMAC')
URL_SODIMAC = config('URL_SODIMAC')
URL_GET_INVENTARIO = config('URL_GET_INVENTARIO')
URL_SET_INVENTARIO = config('URL_SET_INVENTARIO')

# DB
NAME_VAR = config("NAME")
USER_VAR=  config("USER")
PASSWORD_VAR = config("PASSWORD")
HOST_VAR = config("HOST")
PORT_VAR = config("PORT")

# Falabella
FALABELLA_URL = config('FALABELLA_URL')
FALABELLA_API_KEY = config('FALABELLA_API_KEY')

# OTHERS
COLUMNS_SHOPI = ['N/A','Codigo barras','Costo','Precio','Precio comparación','Proveedor','SKU','Stock','Tags','Titulo']

COLUMNS_ALL_PRODUCTS = ["id_variantShopi", "id_product", "title", "tags", "vendor", "status", "price", "compare_at_price", "sku", "barcode", "inventory_quantity", "cursor", "costo", "margen_comparacion_db", "kit", "image_link", "category", "items_number","margen", "commission_seller", "commission_platform", "shipping", "publicity", "aditional"]
COLUMNS_COUNT_RELATIONS = ["id_variantShopi", "id_product", "title", "tags", "vendor", "status", "price", "compare_at_price", "sku", "barcode", "inventory_quantity", "cursor", "margen", "costo", "margen_comparacion_db", "kit", "image_link",'relation_sodi', 'relation_meli']

COLUMNS_SHOPIFY =  ['id_variantShopi', 'id_product', 'sku', 'cost', 'utility', 'items_number', 'commission_seller', 'publicity', 'aditional', 'packaging_cost', 'price_base', 'image_link', 'title', 'inventory_quantity', 'tags', 'vendor', 'status', 'real_price', 'compare_at_price', 'barcode', 'margen_comparacion_db', 'commission_platform', 'category', 'projected_price', 'projected_compare_at_price', 'shipment_cost' ]

APP_ID = config('APP_ID')
CLIENT_SECRET = config('CLIENT_SECRET')
URL_REDIRECT = config('URL_REDIRECT')
URL_GET_TOKEN = config('URL_GET_TOKEN')
USER_ID = config('USER_ID')




	