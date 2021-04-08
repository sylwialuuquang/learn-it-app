from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView

from .views import SignUpView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('sign-up/', SignUpView.as_view(), name='sign-up')
]

