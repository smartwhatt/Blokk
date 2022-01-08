import graphene
from graphene_django import DjangoObjectType
from .models import *

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined', "publickey")

class WalletType(DjangoObjectType):
    class Meta:
        model = Wallet

class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction

class CurrencyType(DjangoObjectType):
    class Meta:
        model = Currency

        



class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.Int())
    user_by_username = graphene.Field(UserType, username=graphene.String())

    all_wallets = graphene.List(WalletType)
    wallet_by_id = graphene.Field(WalletType, id=graphene.Int())
    wallets_by_user = graphene.List(WalletType, user=graphene.String())
    wallets_by_currency = graphene.List(WalletType, currency=graphene.String())

    all_transactions = graphene.List(TransactionType)
    all_currencies = graphene.List(CurrencyType)

    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()
    
    def resolve_user_by_id(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return User.objects.get(pk=id)
        return None
    
    def resolve_user_by_username(self, info, **kwargs):
        username = kwargs.get('username')
        if username is not None:
            return User.objects.get(username=username)
        return None
    
    def resolve_all_wallets(self, info, **kwargs):
        return Wallet.objects.all()
    
    def resolve_wallet_by_id(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Wallet.objects.get(pk=id)
        return None
    
    def resolve_wallets_by_user(self, info, **kwargs):
        user = kwargs.get('user')
        if user is not None:
            return Wallet.objects.filter(user=user)
        return None
    
    def resolve_wallets_by_currency(self, info, **kwargs):
        currency = kwargs.get('currency')
        if currency is not None:
            return Wallet.objects.filter(currency=currency)
        return None


schema = graphene.Schema(query=Query)