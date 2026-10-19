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



# Танзимоти Pagination барои паёмҳо
class MessagePagination(PageNumberPagination):
    # Дар ҳар саҳифа 10 паём нишон дода мешавад
    page_size = 10


# View барои дидан ва сохтани паёмҳои чат
class ChatMessageView(generics.ListCreateAPIView):
    # Serializer барои табдил додани маълумоти паём
    serializer_class = MessageSerializer
    # Танҳо корбари login карда метавонад ба API дастрасӣ дошта бошад
    permission_classes = [IsAuthenticated]
    # Pagination-и боло сохташударо истифода мебарем
    pagination_class = MessagePagination
    # Чатеро меёбем, ки корбари ҳозира иштирокчии он аст
    def get_chat(self):
        # Корбари ҳозираи login карда
        user = self.request.user
        # Чатро аз база меёбем:
        # корбар бояд user_1 ё user_2 бошад
        # id аз URL гирифта мешавад
        # агар чунин чат набошад ё корбар иштирокчии он набошад,
        # хатои 404 бармегардад
        return get_object_or_404(Chat.objects.filter(Q(user_1=user) | Q(user_2=user)),id=self.kwargs['chat_id'])
    # Рӯйхати паёмҳои чати интихобшударо мегирем
    def get_queryset(self):
        # Танҳо паёмҳои ҳамин чатро мегирем
        # order_by('created_at') — аз паёми қадимӣ ба нав
        return Message.objects.filter(chat=self.get_chat()).order_by('created_at')
    # Ҳангоми сохтани паёми нав ин метод иҷро мешавад
    def perform_create(self, serializer):
        # Паёмро ба чати дуруст мепайвандем
        # sender — корбари ҳозираи login карда
        # save() — паёмро дар база нигоҳ медорад
        serializer.save(chat=self.get_chat(),sender=self.request.user)




# View барои нест кардани паём
class MessageDeleteView(generics.DestroyAPIView):
    # Serializer-и барои паём истифодашаванда
    serializer_class = MessageSerializer
    # Танҳо корбари login карда метавонад API-ро истифода барад
    permission_classes = [IsAuthenticated]
    # Муайян мекунем, ки кадом паёмҳоро корбар метавонад нест кунад
    def get_queryset(self):
        # Танҳо паёмҳоеро мегирем, ки фиристандаашон корбари ҳозира аст
        # self.request.user — корбари login карда
        # sender — майдони модели Message, ки фиристандаро нигоҳ медорад
        return Message.objects.filter(sender=self.request.user)




# View барои дидан ва сохтани гурӯҳҳо
class GroupListCreateView(generics.ListCreateAPIView):
    # Serializer барои маълумоти гурӯҳ
    serializer_class = GroupSerializer
    # Танҳо корбари login карда метавонад API-ро истифода барад
    permission_classes = [IsAuthenticated]
    # Рӯйхати гурӯҳҳое, ки корбари ҳозира узви онҳо мебошад
    def get_queryset(self):
        # members__user — аз робитаи members ба майдони user мегузарем
        # self.request.user — корбари ҳозираи login карда
        # distinct() — гурӯҳҳои такрориро дар натиҷа бартараф мекунад
        return Group.objects.filter(members__user=self.request.user).distinct()
    # Ҳангоми сохтани гурӯҳи нав ин метод иҷро мешавад
    def perform_create(self, serializer):
        # Гурӯҳро месозем ва корбари ҳозираро соҳиби он таъин мекунем
        # serializer.save() — объектро дар база нигоҳ медорад
        group = serializer.save(owner=self.request.user)
        # Корбари ҳозираро ба рӯйхати аъзои гурӯҳ илова мекунем
        # group=group — гурӯҳе, ки ҳоло сохта шуд
        # user=self.request.user — соҳиби гурӯҳ
        # role="owner" — нақши корбар ҳамчун соҳиби гурӯҳ
        GroupMember.objects.create(group=group,user=self.request.user,role="owner",)





# View барои дидан, тағйир додан ва нест кардани як гурӯҳ
class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Муайян мекунад, ки маълумоти гурӯҳ чӣ тавр коркард мешавад
    serializer_class = GroupSerializer
    # Танҳо корбари login карда иҷозат дорад
    permission_classes = [IsAuthenticated]
    # Муайян мекунад, ки корбар ба кадом гурӯҳ дастрасӣ дорад
    def get_queryset(self):
        # Корбари ҳозираи login карда
        user = self.request.user
        # Гурӯҳеро иҷозат медиҳад, ки:
        # 1. Корбар соҳиби он аст # Ё # 2. Корбар узви он буда, нақши admin дорад
        return Group.objects.filter(Q(owner=user) | Q(members__user=user, members__role="admin")).distinct()
    # Permission-ро вобаста ба HTTP method интихоб мекунад
    def get_permissions(self):
        # Агар корбар мехоҳад гурӯҳро нест кунад
        if self.request.method == "DELETE":
            # Танҳо корбари login карда ва соҳиби гурӯҳ
            return [IsAuthenticated(),IsGroupOwner()]
        # Агар корбар мехоҳад гурӯҳро тағйир диҳад
        if self.request.method in ("PATCH", "PUT"):
            # Танҳо соҳиби гурӯҳ ё админ
            return [IsAuthenticated(),IsGroupOwnerOrAdmin()]
        # Барои GET ва дигар методҳо танҳо login талаб мешавад
        return [IsAuthenticated()]




# View барои дидан ва илова кардани аъзоёни гурӯҳ
class GroupMemberListCreateView(generics.ListCreateAPIView):
    # Танҳо корбарони login карда метавонанд истифода баранд
    permission_classes = [IsAuthenticated]
    # Маълумоти аъзоён бо ҳамин Serializer коркард мешавад
    serializer_class = GroupMemberSerializer
    # Гурӯҳро аз URL мегирад
    def get_group(self):
        # group_id аз URL гирифта мешавад
        # Масалан: /api/groups/5/members/
        # Агар гурӯҳи рақами 5 набошад, хатои 404 медиҳад
        return get_object_or_404(Group,pk=self.kwargs["group_id"])

    # Рӯйхати аъзоёни гурӯҳро бармегардонад
    def get_queryset(self):
        # Гурӯҳи дархостшударо мегирем
        group = self.get_group()
        # Санҷида мешавад, ки корбари ҳозира узви ҳамин гурӯҳ аст ё не
        is_member = GroupMember.objects.filter(group=group,user=self.request.user).exists()
        # Агар узви гурӯҳ набошад, иҷозат намедиҳем
        if not is_member:
            raise PermissionDenied("Танҳо аъзои гурӯҳ рӯйхати иштирокчиёнро дида метавонанд.")
        # Ҳамаи аъзоёни ҳамин гурӯҳро мегирем
        # select_related() барои кам кардани дархостҳои иловагӣ ба база
        return GroupMember.objects.filter(group=group).select_related("user", "group")
    # Ҳангоми POST аъзои нав илова мешавад
    def perform_create(self, serializer):
        # Гурӯҳеро мегирем, ки ба он аъзо илова мешавад
        group = self.get_group()
        # Корбари ҳозираи login карда
        user = self.request.user
        # Owner метавонад аъзо илова кунад
        # Ё admin-и ҳамин гурӯҳ метавонад ин амалро иҷро кунад
        can_add = (group.owner_id == user.id or GroupMember.objects.filter(group=group,user=user,role="admin").exists())
        # Агар owner ё admin набошад, хатои 403 медиҳем
        if not can_add:
            raise PermissionDenied("Танҳо owner ё admin метавонад аъзо илова кунад.")
        # Корбареро мегирем, ки бояд ба гурӯҳ илова шавад
        # user бояд дар Serializer ҳамчун майдони writeable бошад
        new_user = serializer.validated_data["user"]
        # Санҷида мешавад, ки ин корбар аллакай узви гурӯҳ нест
        if GroupMember.objects.filter(group=group,user=new_user).exists():
            # Агар аллакай узв бошад, хатои validation медиҳем
            raise ValidationError({"user": "Ин корбар аллакай узви гурӯҳ аст."})
        # Аъзои навро дар база сабт мекунем
        # group — гурӯҳи интихобшуда
        # role="member" — нақши оддӣ, на admin
        serializer.save(group=group,role="member")




# View барои тағйир додани нақши аъзои гурӯҳ
class GroupMemberUpdateView(generics.UpdateAPIView):
    # Serializer-и махсус барои нақши аъзо
    serializer_class = GroupMemberRoleSerializer
    # Танҳо корбари login карда метавонад дархост фиристад
    permission_classes = [IsAuthenticated]
    # Танҳо PATCH, HEAD ва OPTIONS иҷозат дода шудаанд
    # PUT ва DELETE дар ин endpoint иҷозат нестанд
    http_method_names = ["patch", "head", "options"]
    # Гурӯҳро аз URL мегирем
    def get_group(self):
        # group_id аз URL гирифта мешавад
        # Агар гурӯҳ ёфт нашавад, хатои 404 медиҳем
        return get_object_or_404(Group,pk=self.kwargs["group_id"])
    # Аъзоёни танҳо ҳамин гурӯҳро интихоб мекунем
    def get_queryset(self):
        # group_id — ID-и гурӯҳ аз URL
        # select_related() барои кам кардани дархостҳои база
        return GroupMember.objects.filter(group_id=self.kwargs["group_id"]).select_related("group", "user")
    # Пеш аз нигоҳ доштани тағйирот иҷозатҳоро месанҷем
    def perform_update(self, serializer):
        # Гурӯҳи дархостшударо мегирем
        group = self.get_group()
        # Санҷида мешавад, ки корбари ҳозира соҳиби гурӯҳ аст ё не
        if group.owner_id != self.request.user.id:
            # Агар owner набошад, тағйиротро манъ мекунем
            raise PermissionDenied("Танҳо соҳиби гурӯҳ метавонад нақшҳоро тағйир диҳад.")
        # Аъзое, ки ҳоло тағйир дода мешавад
        member = serializer.instance
        # Агар ин аъзо худи owner бошад ва нақши нав owner набошад
        if (member.user_id == group.owner_id and serializer.validated_data.get("role", member.role) != "owner"):
            # Тағйир додани нақши owner манъ аст
            raise ValidationError({"role": "Нақши соҳиби гурӯҳро бо ин endpoint тағйир додан мумкин нест."})
        # Агар ҳамаи санҷишҳо гузаранд, маълумотро сабт мекунем
        serializer.save()





# View барои аз гурӯҳ баромадани корбар
class GroupLeaveView(generics.DestroyAPIView):
    # Танҳо корбари login карда метавонад
    permission_classes = [IsAuthenticated]
    # Serializer барои объекти аъзои гурӯҳ
    serializer_class = GroupMemberSerializer
    # Муайян мекунад, ки кадом аъзои гурӯҳ бояд нест карда шавад
    def get_object(self):
        # Гурӯҳро аз ID-и URL меёбем
        group = get_object_or_404(Group,pk=self.kwargs["group_id"])
        # Санҷида мешавад, ки корбари ҳозира соҳиби гурӯҳ аст ё не
        if group.owner_id == self.request.user.id:
            # Owner наметавонад бо ин endpoint аз гурӯҳ барояд
            raise PermissionDenied("Соҳиби гурӯҳ баромада наметавонад. ""Аввал бояд соҳиби нав таъин шавад.")
        # Узвияти худи корбари ҳозираро меёбем
        # Агар узви ин гурӯҳ набошад, хатои 404 медиҳем
        return get_object_or_404(GroupMember,group=group,user=self.request.user)
    # Амали нест кардани узвиятро дар transaction иҷро мекунем
    @transaction.atomic
    def perform_destroy(self, instance):
        # Узвияти корбари ҳозираро аз база нест мекунем
        # Худи гурӯҳ нест намешавад
        instance.delete()



# Pagination барои паёмҳои гурӯҳ
class GroupMessagePagination(PageNumberPagination):
    # Дар ҳар саҳифа 10 паём нишон дода мешавад
    page_size = 10
    # Иҷозат медиҳад, ки клиент шумораи паёмҳоро бо page_size интихоб кунад
    # Масалан: ?page_size=20
    page_size_query_param = "page_size"
    # Шумораи максималии паёмҳо дар як саҳифа 50 аст
    # Клиент наметавонад аз 50 зиёд талаб кунад
    max_page_size = 50


# View барои гирифтани паёмҳо ва фиристодани паёми нав
class GroupMessageListCreateView(generics.ListCreateAPIView):
    # Serializer барои табдил додани маълумоти паём
    serializer_class = GroupMessageSerializer
    # Танҳо корбарони login карда метавонанд истифода баранд
    permission_classes = [IsAuthenticated]
    # Pagination-и махсуси паёмҳои гурӯҳро истифода мебарем
    pagination_class = GroupMessagePagination
    # Гурӯҳро аз ID-и URL меёбем
    def get_group(self):
        # group_id аз URL гирифта мешавад
        # Агар гурӯҳ вуҷуд надошта бошад, хатои 404 медиҳем
        return get_object_or_404(Group,pk=self.kwargs["group_id"])
    # Санҷида мешавад, ки корбари ҳозира узви гурӯҳ аст ё не
    def check_membership(self, group):
        # Узвияти корбарро дар ҳамин гурӯҳ меҷӯем
        # exists() танҳо мавҷуд будани сабтро месанҷад
        is_member = GroupMember.objects.filter(group=group,user=self.request.user).exists()
        # Агар корбар узв набошад, дастрасӣ манъ мешавад
        if not is_member:
            raise PermissionDenied("Танҳо аъзои гурӯҳ метавонанд паёмҳоро истифода баранд.")
    # Рӯйхати паёмҳоеро бармегардонад, ки корбар ҳаққи дидани онҳоро дорад
    def get_queryset(self):
        # Ҳангоми сохтани schema-и Swagger рӯйхати холӣ медиҳем
        if getattr(self, "swagger_fake_view", False):
            return GroupMessage.objects.none()
        # Агар корбар login накарда бошад, рӯйхати холӣ бармегардонем
        # permission_classes низ authentication-ро месанҷад
        if not self.request.user.is_authenticated:
            return GroupMessage.objects.none()
        # Гурӯҳеро мегирем, ки паёмҳояш дархост шудаанд
        group = self.get_group()
        # Санҷида мешавад, ки корбар узви гурӯҳ аст ё не
        self.check_membership(group)
        # Паёмҳои ҳамин гурӯҳро аз база мегирем
        return GroupMessage.objects.filter(group=group).select_related("sender", "group").order_by("-created_at", "-id")
    # Ҳангоми фиристодани паёми нав ин метод иҷро мешавад
    def perform_create(self, serializer):
        # Гурӯҳеро мегирем, ки паём ба он фиристода мешавад
        group = self.get_group()
        # Пеш аз фиристодан узвияти корбарро месанҷем
        self.check_membership(group)
        # Паёмро сабт мекунем
        # group — гурӯҳи паём
        # sender — корбари ҳозираи login карда
        serializer.save(group=group,sender=self.request.user)




# View барои нест кардани паёми гурӯҳ
class GroupMessageDeleteView(generics.DestroyAPIView):
    # Serializer-и паёмро муайян мекунем
    serializer_class = GroupMessageSerializer
    # Танҳо корбари login карда метавонад истифода барад
    permission_classes = [IsAuthenticated]
    # Муайян мекунад, ки кадом паёмро корбар нест карда метавонад
    def get_queryset(self):
        # Ҳангоми сохтани schema-и Swagger рӯйхати холӣ медиҳем
        if getattr(self, "swagger_fake_view", False):
            return GroupMessage.objects.none()
        # Агар корбар login накарда бошад, рӯйхати холӣ медиҳем
        if not self.request.user.is_authenticated:
            return GroupMessage.objects.none()
        # Танҳо паёмҳое, ки худи корбари ҳозира фиристодааст
        return GroupMessage.objects.filter(sender=self.request.user)




# View барои дидани каналҳо ва сохтани канали нав
class ChannelListCreateView(generics.ListCreateAPIView):
    # Serializer барои табдил додани маълумоти канал
    serializer_class = ChannelSerializer
    # Танҳо корбари login карда метавонад ин endpoint-ро истифода барад
    permission_classes = [IsAuthenticated]
    # Рӯйхати каналҳоеро муайян мекунад, ки корбар метавонад бинад
    def get_queryset(self):
        # Ҳангоми сохтани schema-и Swagger рӯйхати холӣ бармегардонем
        if getattr(self, "swagger_fake_view", False):
            return Channel.objects.none()
        # Агар корбар login накарда бошад, танҳо каналҳои public нишон дода мешаванд
        # Эзоҳ: бо IsAuthenticated ин ҳолат одатан дастнорас аст
        if not self.request.user.is_authenticated:
            return Channel.objects.filter(type="public")
        # Барои корбари login карда:
        # каналҳои public ё каналҳое, ки соҳиби онҳо худи ӯст
        return Channel.objects.filter(Q(type="public") | Q(owner=self.request.user)).distinct()
    # Ҳангоми сохтани канал ин метод иҷро мешавад
    def perform_create(self, serializer):
        # Соҳиби каналро ба таври автоматӣ корбари ҳозира таъин мекунем
        serializer.save(owner=self.request.user)



# View барои дидан, тағйир додан ва нест кардани канал
class ChannelDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Serializer барои коркарди маълумоти канал
    serializer_class = ChannelSerializer
    # Танҳо корбарони login карда метавонанд истифода баранд
    permission_classes = [IsAuthenticated]
    # Муайян мекунад, ки кадом канал барои корбар дастрас аст
    def get_queryset(self):
        # Ҳангоми сохтани schema-и Swagger рӯйхати холӣ медиҳем
        if getattr(self, "swagger_fake_view", False):
            return Channel.objects.none()
        # Агар корбар login накарда бошад, канал баргардонида намешавад
        if not self.request.user.is_authenticated:
            return Channel.objects.none()
        # Каналҳои public ё каналҳое, ки соҳиби онҳо корбари ҳозира аст
        return Channel.objects.filter(Q(type="public") | Q(owner=self.request.user)).distinct()
    # Пеш аз тағйир додани канал соҳиби онро месанҷем
    def perform_update(self, serializer):
        # Каналеро мегирем, ки дархост ба он равона шудааст
        channel = self.get_object()
        # Санҷида мешавад, ки корбари ҳозира соҳиби канал аст ё не
        if channel.owner_id != self.request.user.id:
            # Агар соҳиби канал набошад, тағйирот манъ мешавад
            raise PermissionDenied("Только владелец может изменить канал.")
        # Агар соҳиби канал бошад, тағйиротро дар база нигоҳ медорем
        serializer.save()
    # Пеш аз нест кардани канал соҳиби онро месанҷем
    def perform_destroy(self, instance):
        # Агар корбари ҳозира соҳиби канал набошад
        if instance.owner_id != self.request.user.id:
            # Нест кардани канал манъ мешавад
            raise PermissionDenied("Только владелец может удалить канал.")
        # Агар соҳиби канал бошад, каналро аз база нест мекунем
        instance.delete()




# View барои обуна шудан ва бекор кардани обуна
class ChannelFollowView(generics.GenericAPIView):
    # Танҳо корбари login карда метавонад
    permission_classes = [IsAuthenticated]
    # Serializer барои нишон додани маълумоти обуна
    serializer_class = ChannelFollowSerializer
    # POST — обуна шудан ба канал
    def post(self, request, channel_id):
        # Каналро аз ID-и URL меёбем
        # Агар канал набошад, хатои 404 бармегардад
        channel = get_object_or_404(Channel,pk=channel_id)
        # Ба канали private бе иҷозати махсус обуна шудан манъ аст
        if channel.type == "private":
            raise PermissionDenied("Барои обуна шудан ба канали private иҷозат лозим аст.")
        # Transaction кафолат медиҳад, ки амалиёт дуруст иҷро шавад
        try:
            with transaction.atomic():
                # Агар обуна аллакай бошад, created=False
                # Агар обунаи нав сохта шавад, created=True
                follow, created = ChannelFollow.objects.get_or_create(
                    user=request.user,  # Корбари ҳозираи login карда
                    channel=channel    )
        # Агар дар база хатои integrity пайдо шавад
        # Масалан, ҳангоми кӯшиши сохтани обунаи такрорӣ
        except IntegrityError:
            # Обунаи нав сохта нашудааст
            created = False
            # Обунаи мавҷударо меёбем, агар вуҷуд дошта бошад
            follow = ChannelFollow.objects.filter(user=request.user,channel=channel).first()
        # Агар обуна аллакай вуҷуд дошта бошад
        if not created:
            # Хатои 400 — обунаи такрорӣ иҷозат нест
            return Response({"detail": "Шумо аллакай ба ин канал обуна ҳастед."},status=status.HTTP_400_BAD_REQUEST)
        # Обунаи нав сохта шуд: маълумот ва статуси 201 бармегардад
        return Response(self.get_serializer(follow).data,status=status.HTTP_201_CREATED)
    # DELETE — бекор кардани обуна
    def delete(self, request, channel_id):
        # Каналро аз рӯйи ID меёбем
        channel = get_object_or_404(Channel,pk=channel_id)
        # Танҳо обунаи корбари ҳозираро дар ҳамин канал меёбем ва нест мекунем
        # delete() шумораи объектҳои нестшударо бармегардонад
        deleted, _ = ChannelFollow.objects.filter(user=request.user,channel=channel).delete()
        # Агар ягон обуна нест нашуда бошад
        if not deleted:
            # Хатои 404 — корбар ба ин канал обуна нест
            return Response({"detail": "Шумо ба ин канал обуна нестед."},status=status.HTTP_404_NOT_FOUND)
        # 204 — обуна бекор шуд, ҷавоб body надорад
        return Response(status=status.HTTP_204_NO_CONTENT)




# View барои дидани рӯйхати обунаҳои корбари ҳозира
class FollowingListView(generics.ListAPIView):
    # Serializer барои табдил додани обунаҳо ба маълумоти API
    serializer_class = ChannelFollowSerializer
    # Танҳо корбари login карда метавонад рӯйхатро бинад
    permission_classes = [IsAuthenticated]
    # Муайян мекунад, ки кадом обунаҳо баргардонида шаванд
    def get_queryset(self):
        # Ҳангоми сохтани schema-и Swagger рӯйхати холӣ бармегардонем

        if getattr(self, "swagger_fake_view", False):
            return ChannelFollow.objects.none()
        # Танҳо обунаҳои корбари ҳозираро мегирем
        # select_related("channel") — маълумоти каналро бо JOIN мегирем
        # order_by("-created_at") — обунаҳои навтарин аввал нишон дода мешаванд
        return ChannelFollow.objects.filter(user=self.request.user).select_related("channel").order_by("-created_at")


# GenericAPIView барои сохтани API View истифода мешавад
class ChannelIsFollowingView(generics.GenericAPIView):
    # Танҳо корбарони login карда метавонанд истифода баранд
    permission_classes = [IsAuthenticated]
    # Метод GET барои санҷидани подписка истифода мешавад
    def get(self, request, channel_id):
        # Каналро аз база бо ID меёбем
        # Агар канал набошад, хатои 404 бармегардонад
        channel = get_object_or_404(Channel, pk=channel_id)
        # Месанҷем, ки user-и ҳозира ба ҳамин канал подписка шудааст ё не
        # exists() True ё False бармегардонад
        is_following = ChannelFollow.objects.filter(
            user=request.user,  # Танҳо подпискаи user-и ҳозира
            channel=channel,    # Танҳо ба ҳамин канал
        ).exists()              # Агар ёбад True, агар наёбад False
        # Натиҷаро дар шакли JSON бармегардонем
        return Response({
            "channel_id": channel.id,       # ID-и канал
            "is_following": is_following,    # Статуси подписка
        })


# Pagination: дар ҳар саҳифа 10 пост
class PostPagination(PageNumberPagination):
    # Миқдори постҳо дар як саҳифа
    page_size = 10


# POST /api/channels/<channel_id>/posts/
# API барои сохтани пост дар канали муайян
class ChannelPostCreateView(generics.CreateAPIView):

    # Serializer барои санҷидан ва нигоҳ доштани маълумоти пост
    serializer_class = PostSerializer
    # Танҳо корбарони login карда метавонанд
    permission_classes = [IsAuthenticated]
    # Пеш аз сабт кардани пост ин метод иҷро мешавад
    def perform_create(self, serializer):
        # ID-и каналро аз URL мегирем
        channel_id = self.kwargs['channel_id']
        # Каналро аз база меёбем
        # Агар канал вуҷуд надошта бошад, хатои 404 мешавад
        channel = get_object_or_404(Channel, id=channel_id)
        # Санҷиш: оё user-и ҳозира соҳиби канал аст?
        if channel.owner != self.request.user:
            # Агар соҳиби канал набошад, иҷозат намедиҳем
            # HTTP 403 Forbidden
            raise PermissionDenied("Only the channel owner can create posts.")
        # Постро сабт мекунем ва каналро аз URL мегирем
        # User наметавонад channel-и дигарро аз request body фиристад
        serializer.save(channel=channel)



# GET /api/channels/<channel_id>/posts/
# API барои гирифтани рӯйхати постҳои канал
class ChannelPostListView(generics.ListAPIView):
    # Serializer барои табдил додани post ба JSON
    serializer_class = PostSerializer
    # Танҳо user-и login карда метавонад
    permission_classes = [IsAuthenticated]
    # Дар як саҳифа 10 пост нишон медиҳад
    pagination_class = PostPagination
    # QuerySet-и постҳоеро, ки бояд нишон дода шаванд, муайян мекунад
    def get_queryset(self):
        # ID-и каналро аз URL мегирем
        channel_id = self.kwargs['channel_id']
        # Каналро аз база меёбем
        # Агар канал набошад, 404 бармегардад
        channel = get_object_or_404(Channel, id=channel_id)
        # User-и ҳозираро мегирем
        user = self.request.user
        # Санҷиш: user соҳиби канал аст ё не
        is_owner = channel.owner == user
        # Санҷиш: user ба канал подписка шудааст ё не
        is_follower = channel.followers.filter(user=user).exists()
        # Агар канал private бошад ва user соҳиби канал ё follower набошад
        if channel.type == 'private' and not (is_owner or is_follower):
            # Дастрасӣ манъ мешавад — HTTP 403
            raise PermissionDenied("You do not have access to this channel.")

        # Постҳои ҳамин каналро мегирем
        # Постҳои нав аввал меоянд
        return Post.objects.filter(
            channel=channel
        ).order_by('-created_at')



# GET    /api/posts/5/  - гирифтани пости ID=5
# PATCH  /api/posts/5/  - тағйир додани баъзе маълумот
# PUT    /api/posts/5/  - пурра нав кардани маълумот
# DELETE /api/posts/5/  - нест кардани пост
# Retrieve = гирифтани як объект
# Update = тағйир додан
# Destroy = нест кардан
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Serializer барои табдил додани Post ба JSON ва баръакс
    serializer_class = PostSerializer
    # Танҳо user-и login карда метавонад
    permission_classes = [IsAuthenticated]
    # Муайян мекунад, ки кадом постҳо дастрас бошанд
    def get_queryset(self):
        # Танҳо постҳои каналҳоеро мегирем,
        # ки соҳиби онҳо user-и ҳозира мебошад
        return Post.objects.filter(channel__owner=self.request.user)
