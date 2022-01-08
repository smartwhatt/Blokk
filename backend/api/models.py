# Modules import
import rsa

# Django import
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.signing import Signer
# Create your models here.


def pfp_path(instance, filename):
    return f'pfp/{instance.username}/{filename}'

class User(AbstractUser):
    publickey = models.TextField(max_length=5000, blank=True, null=True)
    privatekey = models.TextField(max_length=5000, blank=True, null=True)

    pfp = models.ImageField(upload_to=pfp_path, blank=True, null=True)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']


    def __str__(self):
        return self.username

    def generateKey(self):
        (pubkey, privkey) = rsa.newkeys(2048)
        self.publickey = pubkey.save_pkcs1()
        self.privatekey = privkey.save_pkcs1()
        self.save()
        return (pubkey, privkey)
    
    def create_user(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.generateKey()
        self.save()
        return self
    
    def create_superuser(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_superuser = True
        self.is_staff = True
        self.generateKey()
        self.save()
        return self
    
    def get_publickey(self):
        return self.publickey
    
    def get_privatekey(self):
        return self.privatekey

class Currency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    invite_code = models.CharField(max_length=100, blank=True, null=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')
    market_cap = models.IntegerField(default=-1)
    # ledger = models.ForeignKey('Ledger', on_delete=models.CASCADE, related_name='currencies', blank=True, null=True)


    def __str__(self):
        return self.name

    def generateInvite(self):
        signer = Signer()
        self.invite_code = signer.sign(f"{self.id}-{self.name}-{self.symbol}")
        self.save()
        return self.invite_code
    
    def create(self, name, symbol, admin):
        self.name = name
        self.symbol = symbol
        self.admin = admin
        self.save()
        self.generateInvite()
        return self
    
    def get_users(self):
        return self.wallets.all().values_list('user', flat=True)


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    balance = models.IntegerField(default=0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='wallets')

    def __str__(self):
        return f'{self.user.username}\'s wallet'

    def deposit(self, amount):
        self.balance += amount
        self.save()
        return self.balance
    
    def withdraw(self, amount):
        self.balance -= amount
        self.save()
        return self.balance

class Transaction(models.Model):
    sender = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='receiver')
    amount = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return f'{self.sender.user.username} sent {self.amount} to {self.receiver.user.username}'

    def create(self, sender, receiver, amount, currency):
        if sender.currency == currency and receiver.currency == currency:
            if sender.balance >= amount:
                self.sender = sender
                self.receiver = receiver
                self.amount = amount
                self.currency = currency
                self.save()
                sender.withdraw(amount)
                receiver.deposit(amount)
                return self
        else:
            return None