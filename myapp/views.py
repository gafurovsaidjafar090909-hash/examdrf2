from django.shortcuts import render
from rest_framework import generics
from rest_framework.exceptions import NotFound,ValidationError
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class AccountMeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = AccountSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password changed successfully'},status=200)



class AccountMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = AccountSerializer(request.user)
        return Response(serializer.data)
    

class ProfileCreateView(generics.CreateAPIView):
    serializer_class = ProfileCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated] 
    def get_queryset(self):
        queryset = Profile.objects.select_related('user')
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(username__icontains=search))
        return queryset


class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.select_related('user')



class MyProfileView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'options', 'head']
    def get_object(self):
        try:
            return Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise NotFound('Profile not found. Create a profile first.')



class AvatarCreateView(generics.CreateAPIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


class AvatarDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Avatar.objects.none()

        if not self.request.user.is_authenticated:
            return Avatar.objects.none()

        return Avatar.objects.filter(
            profile=self.request.user.profile
        )




class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(Q(user_1=user) | Q(user_2=user))
    def perform_create(self, serializer):
        user_2_id = self.request.data.get('user_2')
        try:
            user_2 = Account.objects.get(id=user_2_id)
        except (Account.DoesNotExist, ValueError, TypeError):
            raise ValidationError({'user_2': 'User not found.'})
        if user_2 == self.request.user:
            raise ValidationError('You cannot create a chat with yourself.')
        chat = Chat.objects.filter(
            Q(user_1=self.request.user, user_2=user_2) |
            Q(user_1=user_2, user_2=self.request.user)).first()

        if chat:
            raise ValidationError('Chat already exists.')
        serializer.save(user_1=self.request.user, user_2=user_2)



class ChatDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Avatar.objects.none()

        if not self.request.user.is_authenticated:
            return Avatar.objects.none()

        return Avatar.objects.filter(
            profile=self.request.user.profile
        )
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated


class MessagePagination(PageNumberPagination):
    page_size = 10


class ChatMessageView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination

    def get_chat(self):
        user = self.request.user

        return get_object_or_404(
            Chat.objects.filter(
                Q(user_1=user) | Q(user_2=user)
            ),
            id=self.kwargs['chat_id']
        )

    def get_queryset(self):
        return Message.objects.filter(
            chat=self.get_chat()
        ).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(
            chat=self.get_chat(),
            sender=self.request.user
        )


class MessageDeleteView(generics.DestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            sender=self.request.user
        )


from .permissions import IsGroupOwner, IsGroupOwnerOrAdmin


class GroupListCreateView(generics.ListCreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(members__user=self.request.user).distinct()
    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        GroupMember.objects.create(group=group,user=self.request.user,role="owner",)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(Q(owner=user) | Q(members__user=user, members__role="admin")).distinct()
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsGroupOwner()]
        
        if self.request.method in ("PATCH", "PUT"):
            return [IsAuthenticated(), IsGroupOwnerOrAdmin()]

        return [IsAuthenticated()]