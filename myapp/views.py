from django.shortcuts import render
from rest_framework import generics
from .serializers import RegisterSerializer,AccountSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class AccountMeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = AccountSerializer(request.user)
        return Response(serializer.data)