from django.urls import path
from . import views


urlpatterns = [
    path("signup/", views.user_signup, name="user_signup"),
    path("login/", views.user_login, name="user_login"),
    path("profile/", views.user_profile, name="user_profile"),
    path("logout/", views.user_logout, name="user_logout"),
]
