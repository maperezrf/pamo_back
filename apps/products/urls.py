from . import views
from django.urls import path

app_name = 'products'

urlpatterns = [
    path("update", views.update, name="update"),
    path("delete_db", views.delete, name="delete"),
    path("charge_data_meli", views.charge_data_meli, name="charge_data_meli"),
    path("charge_data_sodi", views.charge_data_sodi, name="charge_data_sodi"),
    path("test", views.test, name="test"),
]