from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.admin_login, name="admins_login"),
    path("logout/", views.admin_logout, name="admins_logout"),
    path("home/", views.admin_home, name="admins_home"),
    path("user/add/", views.add_user, name="admins_add_user"),
    path("user/delete/<int:user_id>/", views.delete_user, name="admins_delete_user"),
    path("user/edit/<int:user_id>/", views.edit_user, name="admins_edit_user"),
    path("products/", views.admin_products, name="admins_products"),
    path("products/add/", views.admin_add_product, name="admins_add_product"),
    path("products/edit/<int:id>/", views.admin_edit_product, name="admins_edit_product"),
    path("products/delete/<int:id>/", views.admin_delete_product, name="admins_delete_product"),
    path("account/", views.user_profile, name="admins_account"),
]
