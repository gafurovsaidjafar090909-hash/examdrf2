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

    path('avatars/', AvatarCreateView.as_view(), name='avatar-create'),
    path('avatars/<int:pk>/', AvatarDetailView.as_view(), name='avatar-detail'),

    path('chats/', ChatListCreateView.as_view(), name='chat-list-create'),
    path('chats/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),

     # GET: дидани паёмҳо
    # POST: фиристодани паём
    path('chats/<int:chat_id>/messages/',ChatMessageView.as_view(),name='chat-messages'),
    # DELETE: нест кардани паёми худ
    path('messages/<int:pk>/',MessageDeleteView.as_view(),name='message-delete'),

    path("groups/",GroupListCreateView.as_view(),name="group-list-create",),
    path("groups/<int:pk>/",GroupDetailView.as_view(),name="group-detail",),
]