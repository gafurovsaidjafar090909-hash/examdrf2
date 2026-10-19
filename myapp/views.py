from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.exceptions import NotFound,ValidationError,PermissionDenied
from .serializers import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from .permissions import IsGroupOwner, IsGroupOwnerOrAdmin
from django.db import transaction,IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination



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



# ListAPIView — барои нишон додани рӯйхати объектҳо истифода мешавад
class ProfileListView(generics.ListAPIView):
    # Serializer-и истифодашаванда барои табдил додани профилҳо
    serializer_class = ProfileSerializer
    # Танҳо корбари аутентификатсияшуда метавонад ба ин API дастрасӣ дошта бошад
    permission_classes = [IsAuthenticated]
    # Ин метод муайян мекунад, ки кадом профилҳо аз база гирифта шаванд
    def get_queryset(self):
        # Ҳамаи профилҳоро мегирем
        # select_related('user') маълумоти user-ро бо JOIN мегирад,
        # то барои ҳар профил дархости иловагӣ ба база кам шавад
        queryset = Profile.objects.select_related('user')
        # Қимати search-ро аз URL мегирем
        # Масалан: /profiles/?search=ali
        search = self.request.query_params.get("search")
        # Агар search холӣ набошад, ҷустуҷӯ мекунем
        if search:
            # Ҷустуҷӯ аз рӯйи first_name ё last_name ё username
            # Q ва аломати | маънои OR доранд
            # icontains — ҷустуҷӯи матн бе фарқ кардани ҳарфҳои калон ва хурд
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search)
            )
        # Рӯйхати профилҳои ёфтшударо бармегардонем
        return queryset



class ProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.select_related('user')




# View барои тағйир додани профили корбари ҳозира
class MyProfileView(generics.UpdateAPIView):
    # Serializer-и барои профил истифодашаванда
    serializer_class = ProfileSerializer
    # Танҳо корбари login карда метавонад ин API-ро истифода барад
    permission_classes = [IsAuthenticated]
    # Танҳо PATCH, OPTIONS ва HEAD иҷозат дода мешаванд
    # PUT, POST ва DELETE иҷозат дода намешаванд
    http_method_names = ['patch', 'options', 'head']
    # Муайян кардани профиле, ки бояд тағйир дода шавад
    def get_object(self):
        # Кӯшиш мекунем профили корбари ҳозираро ёбем
        try:
            return Profile.objects.get(user=self.request.user)
        # Агар чунин профил вуҷуд надошта бошад
        except Profile.DoesNotExist:
            # Хатои 404 бармегардонем
            # Паём мегӯяд, ки аввал профил сохтан лозим аст
            raise NotFound('Profile not found. Create a profile first.')




# View барои сохтани Avatar-и нав
class AvatarCreateView(generics.CreateAPIView):
    # Serializer барои коркарди маълумоти Avatar
    serializer_class = AvatarSerializer
    # Танҳо корбари login карда метавонад Avatar созад
    permission_classes = [IsAuthenticated]
    # Пеш аз нигоҳ доштани Avatar ин метод иҷро мешавад
    def perform_create(self, serializer):
        # serializer.save() — Avatar-ро дар база нигоҳ медорад
        # profile=self.request.user.profile — Avatar-ро ба профили
        # корбари ҳозираи login карда пайваст мекунад
        serializer.save(profile=self.request.user.profile)


# View барои дидан ва нест кардани Avatar
class AvatarDetailView(generics.RetrieveDestroyAPIView):
    # Serializer барои коркарди маълумоти Avatar
    serializer_class = AvatarSerializer
    # Танҳо корбари login карда метавонад API-ро истифода барад
    permission_classes = [IsAuthenticated]
    # Муайян кардани Avatar-ҳое, ки корбар ба онҳо дастрасӣ дорад
    def get_queryset(self):
        # Агар Swagger View-ро танҳо барои сохтани ҳуҷҷатҳо тафтиш кунад,
        # рӯйхати холӣ бармегардонем, то ба request.user ниёз нашавад
        if getattr(self, 'swagger_fake_view', False):
            return Avatar.objects.none()
        # Агар корбар login накарда бошад, рӯйхати холӣ бармегардонем
        if not self.request.user.is_authenticated:
            return Avatar.objects.none()
        # Танҳо Avatar-ҳоеро мегирем, ки ба профили корбари ҳозира тааллуқ доранд
        # Ин ба пешгирии дастрасӣ ба Avatar-и дигарон кӯмак мекунад
        return Avatar.objects.filter(profile=self.request.user.profile)




# View барои дидани чатҳо ва сохтани чати нав
class ChatListCreateView(generics.ListCreateAPIView):
    # Serializer барои коркарди маълумоти Chat
    serializer_class = ChatSerializer
    # Танҳо корбари login карда метавонад ин API-ро истифода барад
    permission_classes = [IsAuthenticated]
    # Муайян кардани рӯйхати чатҳое, ки корбари ҳозира иштирокчии он аст
    def get_queryset(self):
        # Корбари ҳозираи login карда
        user = self.request.user
        # Чатҳое, ки корбар иштирокчии якум ё дуюм аст
        # Q(...) | Q(...) маънои OR (ё)-ро дорад
        return Chat.objects.filter(Q(user_1=user) | Q(user_2=user))
    # Ин метод ҳангоми сохтани чати нав иҷро мешавад
    def perform_create(self, serializer):
        # ID-и корбари дуюмро аз маълумоти POST мегирем
        user_2_id = self.request.data.get('user_2')
        # Кӯшиш мекунем корбари дуюмро аз база ёбем
        try:
            user_2 = Account.objects.get(id=user_2_id)
        # Агар корбар ёфт нашавад ё ID нодуруст бошад
        except (Account.DoesNotExist, ValueError, TypeError):
            # Хатои 400 бо паёми фаҳмо бармегардонем
            raise ValidationError({'user_2': 'User not found.'})
        # Корбар наметавонад бо худаш чат созад
        if user_2 == self.request.user:
            raise ValidationError('You cannot create a chat with yourself.')
        # Санҷиш мекунем, ки байни ин ду корбар чат аллакай вуҷуд дорад ё не
        # Ҳолати якум: корбари ҳозира user_1 аст
        # Ҳолати дуюм: корбари ҳозира user_2 аст
        # Ин ду шарт барои онанд, ки чат дар ҳар ду тартиб ҷустуҷӯ шавад
        chat = Chat.objects.filter(Q(user_1=self.request.user, user_2=user_2) | Q(user_1=user_2, user_2=self.request.user)).first()
        # Агар чат аллакай вуҷуд дошта бошад, чати такрорӣ намесозем
        if chat:
            raise ValidationError('Chat already exists.')

        # Агар ҳамаи санҷишҳо гузаранд, чатро дар база нигоҳ медорем
        # user_1 — корбари ҳозираи login карда
        # user_2 — корбари интихобшуда
        serializer.save(user_1=self.request.user,user_2=user_2)


# View барои дидан ва нест кардани як чат
class ChatDetailView(generics.RetrieveDestroyAPIView):
    # Serializer барои коркарди маълумоти Chat
    serializer_class = ChatSerializer
    # Танҳо корбари login карда метавонад ин API-ро истифода барад
    permission_classes = [IsAuthenticated]
    # Муайян мекунад, ки корбар ба кадом чатҳо дастрасӣ дорад
    def get_queryset(self):
        # Агар Swagger танҳо ҳуҷҷатҳои API-ро созад,
        # QuerySet-и холӣ бармегардонем
        if getattr(self, 'swagger_fake_view', False):
            return Chat.objects.none()
        # Агар корбар login накарда бошад,
        # ягон чатро дастрас намекунем
        if not self.request.user.is_authenticated:
            return Chat.objects.none()
        # Танҳо чатҳоеро мегирем, ки корбари ҳозира иштирокчии он аст
        # user_1 — иштирокчии якум
        # user_2 — иштирокчии дуюм
        return Chat.objects.filter(Q(user_1=self.request.user) | Q(user_2=self.request.user))



class MessagePagination(PageNumberPagination):
    page_size = 10


class ChatMessageView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination
    def get_chat(self):
        user = self.request.user
        return get_object_or_404(Chat.objects.filter(Q(user_1=user) | Q(user_2=user)),id=self.kwargs['chat_id'])
    def get_queryset(self):
        return Message.objects.filter(chat=self.get_chat()).order_by('created_at')
    def perform_create(self, serializer):
        serializer.save(chat=self.get_chat(),sender=self.request.user)


class MessageDeleteView(generics.DestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)




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




class GroupMemberListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupMemberSerializer
    def get_group(self):
        return get_object_or_404(Group,pk=self.kwargs["group_id"])
    def get_queryset(self):
        group = self.get_group()
        is_member = GroupMember.objects.filter(group=group,user=self.request.user).exists()
        if not is_member:
            raise PermissionDenied("Танҳо аъзои гурӯҳ рӯйхати иштирокчиёнро дида метавонанд.")
        return GroupMember.objects.filter(group=group).select_related("user", "group")
    def perform_create(self, serializer):
        group = self.get_group()
        user = self.request.user
        can_add = (group.owner_id == user.id or GroupMember.objects.filter(group=group,user=user,role="admin").exists())
        if not can_add:
            raise PermissionDenied("Танҳо owner ё admin метавонад аъзо илова кунад.")
        new_user = serializer.validated_data["user"]
        if GroupMember.objects.filter(group=group,user=new_user).exists():
            raise ValidationError({"user": "Ин корбар аллакай узви гурӯҳ аст."})
        serializer.save(group=group,role="member")


class GroupMemberUpdateView(generics.UpdateAPIView):
    serializer_class = GroupMemberRoleSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch", "head", "options"]
    def get_group(self):
        return get_object_or_404(Group,pk=self.kwargs["group_id"])
    def get_queryset(self):
        return GroupMember.objects.filter(group_id=self.kwargs["group_id"]).select_related("group", "user")
    def perform_update(self, serializer):
        group = self.get_group()
        if group.owner_id != self.request.user.id:
            raise PermissionDenied("Танҳо соҳиби гурӯҳ метавонад нақшҳоро тағйир диҳад.")
        member = serializer.instance
        if (member.user_id == group.owner_id and serializer.validated_data.get("role", member.role) != "owner"):
            raise ValidationError({"role": "Нақши соҳиби гурӯҳро бо ин endpoint тағйир додан мумкин нест."})
        serializer.save()


class GroupLeaveView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupMemberSerializer
    def get_object(self):
        group = get_object_or_404(Group,pk=self.kwargs["group_id"])
        if group.owner_id == self.request.user.id:
            raise PermissionDenied("Соҳиби гурӯҳ баромада наметавонад. Аввал бояд соҳиби нав таъин шавад.")
        return get_object_or_404(GroupMember,group=group,user=self.request.user)
    @transaction.atomic
    def perform_destroy(self, instance):
        instance.delete()



class GroupMessagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class GroupMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = GroupMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = GroupMessagePagination
    def get_group(self):
        return get_object_or_404(Group,pk=self.kwargs["group_id"],)
    def check_membership(self, group):
        is_member = GroupMember.objects.filter(group=group,user=self.request.user,).exists()
        if not is_member:
            raise PermissionDenied("Танҳо аъзои гурӯҳ метавонанд паёмҳоро истифода баранд.")
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return GroupMessage.objects.none()
        if not self.request.user.is_authenticated:
            return GroupMessage.objects.none()
        group = self.get_group()
        self.check_membership(group)
        return GroupMessage.objects.filter(group=group).select_related("sender", "group").order_by("-created_at", "-id")
    def perform_create(self, serializer):
        group = self.get_group()
        self.check_membership(group)
        serializer.save(group=group,sender=self.request.user,)


class GroupMessageDeleteView(generics.DestroyAPIView):
    serializer_class = GroupMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return GroupMessage.objects.none()
        if not self.request.user.is_authenticated:
            return GroupMessage.objects.none()
        return GroupMessage.objects.filter(sender=self.request.user)


class ChannelListCreateView(generics.ListCreateAPIView):
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Channel.objects.none()
        if not self.request.user.is_authenticated:
            return Channel.objects.filter(type="public")
        return Channel.objects.filter(Q(type="public") | Q(owner=self.request.user)).distinct()
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ChannelDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Channel.objects.none()
        if not self.request.user.is_authenticated:
            return Channel.objects.none()
        return Channel.objects.filter(Q(type="public") | Q(owner=self.request.user)).distinct()
    def perform_update(self, serializer):
        channel = self.get_object()
        if channel.owner_id != self.request.user.id:
            raise PermissionDenied("Только владелец может изменить канал.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.owner_id != self.request.user.id:
            raise PermissionDenied("Только владелец может удалить канал.")
        instance.delete()





class ChannelFollowView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChannelFollowSerializer
    def post(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        if channel.type == "private":
            raise PermissionDenied("Барои обуна шудан ба канали private иҷозат лозим аст.")
        try:
            with transaction.atomic():
                follow, created = ChannelFollow.objects.get_or_create(user=request.user,channel=channel,)
        except IntegrityError:
            created = False
            follow = ChannelFollow.objects.filter(user=request.user,channel=channel,).first()
        if not created:
            return Response({"detail": "Шумо аллакай ба ин канал обуна ҳастед."},status=status.HTTP_400_BAD_REQUEST,)
        return Response(
            self.get_serializer(follow).data,status=status.HTTP_201_CREATED,)
    def delete(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        deleted, _ = ChannelFollow.objects.filter(user=request.user,channel=channel,).delete()
        if not deleted:
            return Response({"detail": "Шумо ба ин канал обуна нестед."},status=status.HTTP_404_NOT_FOUND,)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowingListView(generics.ListAPIView):
    serializer_class = ChannelFollowSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ChannelFollow.objects.none()
        return ChannelFollow.objects.filter(user=self.request.user).select_related("channel").order_by("-created_at")


class ChannelIsFollowingView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        is_following = ChannelFollow.objects.filter(user=request.user,channel=channel,).exists()
        return Response({"channel_id": channel.id,"is_following": is_following,})






# Pagination: 10 posts per page
class PostPagination(PageNumberPagination):
    page_size = 10


# POST /api/channels/<channel_id>/posts/
class ChannelPostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        channel_id = self.kwargs['channel_id']
        channel = get_object_or_404(Channel,id=channel_id)
        # Only channel owner can create posts
        if channel.owner != self.request.user:
            raise PermissionDenied("Only the channel owner can create posts.")
        # Channel is taken from URL, not from request body
        serializer.save(channel=channel)


# GET /api/channels/<channel_id>/posts/
class ChannelPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    def get_queryset(self):
        channel_id = self.kwargs['channel_id']
        channel = get_object_or_404(Channel,id=channel_id)
        user = self.request.user
        # Check access to private channels
        is_owner = channel.owner == user
        is_follower = channel.followers.filter(user=user).exists()
        if channel.type == 'private' and not (is_owner or is_follower):
            raise PermissionDenied("You do not have access to this channel.")
        # Newest posts first
        return Post.objects.filter(channel=channel).order_by('-created_at')


# GET /api/posts/<id>/
# PATCH /api/posts/<id>/
# DELETE /api/posts/<id>/
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Only posts belonging to the user's own channels
        return Post.objects.filter(channel__owner=self.request.user)
