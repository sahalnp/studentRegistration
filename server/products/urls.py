from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="user_home"),
    path('products/',views.user_products,name="user_products" ),
    path("product/filter/",views.filter_products,name="user_filter_products")
]
