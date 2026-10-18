from django.urls import path
from .views import RegisterView,AccountMeView
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/token/', TokenObtainPairView.as_view(), name='token'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/me/', AccountMeView.as_view(), name='account_me'),
]