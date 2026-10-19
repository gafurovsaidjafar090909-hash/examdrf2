from rest_framework import serializers
from .models import *


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id","phone_number"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = Account
        fields = ['id', 'phone_number', 'password']
    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)
    


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({'old_password': 'Old password is wrong'})
        return data
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AccountMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'phone_number',"password"]
        read_only_fields = fields




class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id',read_only=True)
    class Meta:
        model = Profile
        fields = ['id','user_id','first_name','last_name','username','bio',]
        read_only_fields = ['id', 'user_id']


class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'username', 'bio']


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ['id', 'image']


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'user_1', 'user_2', 'created_at']
        read_only_fields = ['id', 'user_1', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'created_at']
        read_only_fields = ['id', 'chat', 'sender', 'created_at']



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id","title","avatar","owner","created_at",]
        read_only_fields = ["id", "owner", "created_at"]



class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ["id", "group", "user", "role"]
        read_only_fields = ["id", "group", "role"]


class GroupMemberRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ["id", "group", "user", "role"]
        read_only_fields = ["id", "group", "user"]





class GroupMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = ["id","group","sender","content","created_at",]
        read_only_fields = ["id","group","sender","created_at",]



class ChannelSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner_id")
    invite_link = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ["id","title","description","type","owner","invite_link","created_at",]
        read_only_fields = ["id", "owner", "invite_link", "created_at"]
    def get_invite_link(self, obj):
        if obj.type == "public" and obj.invite_link:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(f"/channels/join/{obj.invite_link}/")
            return str(obj.invite_link)
        return None





class ChannelFollowSerializer(serializers.ModelSerializer):
    channel_title = serializers.CharField(source="channel.title",read_only=True,)
    channel_type = serializers.CharField(source="channel.type",read_only=True,)
    class Meta:
        model = ChannelFollow
        fields = ["id","channel","channel_title","channel_type","created_at",]
        read_only_fields = fields
