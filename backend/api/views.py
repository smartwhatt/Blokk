from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response# Create your views here.

from .models import *

@api_view(['GET'])
def index(request):
    return Response({'message': 'Hello, world!'})

@api_view(['POST'])
def register(request):
    username = request.data['username']
    email = request.data['email']
    password = request.data['password']
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    return Response({'message': 'User created successfully'})