from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('healthcheck', views.index, name='healthcheck'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
    path('verify', views.verify, name='verify'),
    path("logout", views.logout, name="logout"),

    path("currency", views.currency, name="currency"),
    path("currency/join", views.currency_join, name="currency_join"),
    path("currency/leave", views.currency_leave, name="currency_leave"),
]
