from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError, Token

from .serializers import *
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


@api_view(['GET', 'POST'])
def verify(request):
    # print("Hallo")
    if request.method == 'POST':
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
    else:

        if request.user.is_authenticated:
            return Response({
                'username': request.user.username,
                'email': request.user.email
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout(request):
    refresh = RefreshToken(request.data['refresh'])
    refresh.blacklist()
    return Response({'message': 'Logged out'}, status=status.HTTP_205_RESET_CONTENT)

# API view for creating currency


@api_view(['POST'])
def currency(request):
    # access = request.headers['Authorization']
    if request.user.is_authenticated:
        # token = AccessToken(access)
        # user = User.objects.get(id=token.payload['user_id'])
        user = request.user
        currency_name = request.data['name']
        currency_symbol = request.data['symbol']
        currency = Currency(name=currency_name,
                            symbol=currency_symbol, admin=user)
        currency.save()

        if request.data.get('market_cap'):
            market_cap = request.data['market_cap']
            currency.market_cap = market_cap
        
        if currency.market_cap == -1:
            if request.data.get('initial_balance'):
                initial_balance = request.data['initial_balance']
                currency.initial_balance = initial_balance
            else:
                return Response({'message': 'Initial balance is required for currency without market cap'}, status=status.HTTP_400_BAD_REQUEST)
        

        currency.save()
        serializer = CurrencySerializers(currency)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    else:
        return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


# API view for joining currency
@api_view(['POST'])
def currency_join(request):
    if request.user.is_authenticated:
        user = request.user
        invite_code = request.data['invite_code']
        try:
            currency = Currency.objects.get(invite_code=invite_code)
        except Currency.DoesNotExist:
            return Response({'message': 'Invalid invite code'}, status=status.HTTP_404_NOT_FOUND)
        wallet = Wallet(user=user, currency=currency, balance=0)
        wallet.save()
        walletSerializer = WalletSerializers(wallet)
        currencySerializer = CurrencySerializers(currency)
        return Response({
            'wallet': walletSerializer.data,
            'currency': currencySerializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def currency_leave(request):
    if request.user.is_authenticated:
        walletid = request.data['wallet']
        try:
            wallet = Wallet.objects.get(id=walletid)
        except Wallet.DoesNotExist:
            return Response({'message': 'Invalid wallet id'}, status=status.HTTP_404_NOT_FOUND)

        if wallet.user == request.user:
            if wallet.balance > 0:
                return Response({'message': 'You cannot leave a currency with a balance'}, status=status.HTTP_400_BAD_REQUEST)
            wallet.delete()
            return Response({'message': 'Left currency'}, status=status.HTTP_200_OK)
        return Response({'message': 'You are not the owner of this wallet'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def wallet_create(request):
    if request.user.is_authenticated:
        user = request.user
        currencyid = request.data['currency']
        try:
            currency = Currency.objects.get(id=currencyid)
        except Currency.DoesNotExist:
            return Response({'message': 'Invalid currency id'}, status=status.HTTP_404_NOT_FOUND)
        wallet = Wallet(user=user, currency=currency, balance=currency.initial_balance)
        wallet.save()
        walletSerializer = WalletSerializers(wallet)
        currencySerializer = CurrencySerializers(currency)
        return Response({
            'wallet': walletSerializer.data,
            'currency': currencySerializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)