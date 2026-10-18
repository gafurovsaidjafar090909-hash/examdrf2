from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

class AccountManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(phone_number, password, **extra_fields)




class Account(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=50, unique=True)
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = AccountManager()

    def __str__(self):
        return self.phone_number


class Profile(models.Model):
    user = models.OneToOneField(Account,on_delete=models.CASCADE,related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=150, unique=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username



class Avatar(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='avatars')
    image = models.CharField(max_length=255)

    def __str__(self):
        return self.profile.username



class Chat(models.Model):
    user_1 = models.ForeignKey(Account,on_delete=models.CASCADE,related_name='chats_1')
    user_2 = models.ForeignKey(Account,on_delete=models.CASCADE,related_name='chats_2')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user_1', 'user_2'],name='unique_chat_pair')]

    def __str__(self):
        return f'{self.user_1} - {self.user_2}'



class Message(models.Model):
    chat = models.ForeignKey(Chat,on_delete=models.CASCADE,related_name='messages')
    sender = models.ForeignKey(Account,on_delete=models.CASCADE,related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender





class Group(models.Model):
    title = models.CharField(max_length=150)
    avatar = models.CharField(max_length=255, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="owned_groups",)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class GroupMember(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    ]
    group = models.ForeignKey(Group,on_delete=models.CASCADE,related_name="members",)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="group_memberships",)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default="member",)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["group", "user"],name="unique_group_member",)]

    def __str__(self):
        return f"{self.user} - {self.group} ({self.role})"