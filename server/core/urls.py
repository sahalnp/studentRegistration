from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("account/",include("accounts.urls")),
    path("user/",include("products.urls")),
    path("admins/",include("admins.urls"))
]

