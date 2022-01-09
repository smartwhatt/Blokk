from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def authenticated_as_user(request):
    if request.user.is_authenticated:
        serializer = UserSerializers(request.user)
        return Response(serializer.data)
    else:
        return Response({'message': 'User is not authenticated'})