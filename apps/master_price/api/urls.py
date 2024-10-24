from apps.master_price.api import api
from django.urls import path

urlpatterns = [
    path("list_products/", api.masterPriceAPIView.as_view(), name="list_products"),
    path("oaut_meli/", api.OAuthAPIView.as_view(), name="oaut_meli"),
    path("notification_product_shopi/", api.NotificationProductShopy.as_view(), name="wh_shopi"),
    path("notification_create_order_shopi/", api.NotificationCreateOrderShopify.as_view(), name="create_order_shopi"),
    path("notification_update_meli/", api.NotificationHandlerMeli.as_view(), name="wh_meli"),
    path("notification_delete_shopi/", api.NotificationDeleteShopífy.as_view(), name="wh_delete_shopi"),
    path("connection_sheets/<str:process>/", api.ConnectionSheets.as_view(), name= "conn_sheets"),
    path("connection_sheets/", api.ConnectionSheets.as_view(), name= "conn_sheets"),
    path("connection_shopify/", api.ConnectionShopify.as_view(), name= "conn_shopi"),
]