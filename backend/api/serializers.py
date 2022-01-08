from .models import *
from rest_framework.serializers import ModelSerializer



class UserSerializers(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.generateKey()
        user.save()
        return user

class CurrencySerializers(ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'name', 'symbol', 'admin')

class WalletSerializers(ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('id', 'currency', 'user', 'balance')

class TransactionSerializers(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'sender', 'receiver', 'amount', 'currency')
