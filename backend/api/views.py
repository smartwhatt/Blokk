from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError, Token

from .serializers import UserSerializers
from .models import *

# Create your views here.


@api_view(['GET'])
def index(request):
    return Response({'message': 'Hello, world!'})


@api_view(['POST'])
def register(request):
    username = request.data['username']
    email = request.data['email']
    password = request.data['password']
    user = User.objects.create_user(
        username=username, email=email, password=password)
    user.save()
    
    refresh = RefreshToken.for_user(user)
    access = AccessToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(access)
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    username = request.data['username']
    password = request.data['password']
    user = User.objects.get(username=username)
    if user is None:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    if user.check_password(password):
        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(access)
        }
        return Response(token, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def verify(request):
    access = request.data['access']
    try:
        token = AccessToken(access)
        user = User.objects.get(id=token.payload['user_id'])
        return Response({
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_200_OK)
    except TokenError:
        return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout(request):
    refresh = RefreshToken(request.data['refresh'])
    refresh.blacklist()
    return Response({'message': 'Logged out'}, status=status.HTTP_205_RESET_CONTENT)