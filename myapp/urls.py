from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/token/', TokenObtainPairView.as_view(), name='token'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/me/', AccountMeView.as_view(), name='account_me'),
    path('accounts/change-password/',ChangePasswordView.as_view(),name='change_password'),

    path('profiles/',ProfileListView.as_view(),name='profile-list'),
    path('profiles/me/',MyProfileView.as_view(),name='my-profile'),
    path('profiles/<int:pk>/',ProfileDetailView.as_view(),name='profile-detail'),
    path('profiles/create/', ProfileCreateView.as_view(), name='profile-create'),
]