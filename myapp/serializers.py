from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id","phone_number"]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id","phone_number","password"]
    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)
