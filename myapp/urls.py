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

     
    path('chats/<int:chat_id>/messages/',ChatMessageView.as_view(),name='chat-messages'),
    path('messages/<int:pk>/',MessageDeleteView.as_view(),name='message-delete'),

    path("groups/", GroupListCreateView.as_view(), name="group-list-create"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group-detail"),
    path("groups/<int:group_id>/members/",GroupMemberListCreateView.as_view(),name="group-members",),
    path("groups/<int:group_id>/members/<int:pk>/",GroupMemberUpdateView.as_view(),name="group-member-update",),
    path("groups/<int:group_id>/members/me/",GroupLeaveView.as_view(),name="group-leave",),
    path("groups/<int:group_id>/messages/",GroupMessageListCreateView.as_view(),name="group-message-list-create",),
    path("group-messages/<int:pk>/",GroupMessageDeleteView.as_view(),name="group-message-delete",),

path(
    "channels/",
    ChannelListCreateView.as_view(),
    name="channel-list-create",
),
path(
    "channels/<int:pk>/",
    ChannelDetailView.as_view(),
    name="channel-detail",
),


path(
    "channels/<int:channel_id>/follow/",
    ChannelFollowView.as_view(),
    name="channel-follow",
),
path(
    "following/",
    FollowingListView.as_view(),
    name="following-list",
),
path(
    "channels/<int:channel_id>/is-following/",
    ChannelIsFollowingView.as_view(),
    name="channel-is-following",
),


    path(
        'channels/<int:channel_id>/posts/',
        ChannelPostCreateView.as_view(),
        name='channel-post-create',
    ),

    # List posts in a channel
    path(
        'channels/<int:channel_id>/posts/',
        ChannelPostListView.as_view(),
        name='channel-post-list',
    ),

    # Retrieve, update, delete a post
    path(
        'posts/<int:pk>/',
        PostDetailView.as_view(),
        name='post-detail',
    ),
    
]


    
    