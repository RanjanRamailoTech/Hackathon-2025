from django.urls import path
from .views import CompanySignupView, CompanyLoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup/", CompanySignupView.as_view(), name="company-signup"),
    path("login/", CompanyLoginView.as_view(), name="company-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]