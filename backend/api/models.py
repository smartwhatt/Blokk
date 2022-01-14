# Modules import
# import rsa
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
import binascii



# Django import
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.signing import Signer
# Create your models here.


def pfp_path(instance, filename):
    return f'pfp/{instance.username}/{filename}'


class User(AbstractUser):
    pfp = models.ImageField(
        upload_to=pfp_path, blank=True, null=True, default=None)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    def __str__(self):
        return self.username

    

    def create_user(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.save()
        return self

    def create_superuser(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_superuser = True
        self.is_staff = True
        self.save()
        return self


class Currency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    invite_code = models.CharField(max_length=100, blank=True, null=True)
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='admin')
    market_cap = models.IntegerField(default=-1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    initial_balance = models.IntegerField(default=0)
    # ledger = models.ForeignKey('Ledger', on_delete=models.CASCADE, related_name='currencies', blank=True, null=True)

    def __str__(self):
        return self.name

    def generateInvite(self):
        signer = Signer()
        self.invite_code = signer.sign(f"{self.id}-{self.name}-{self.symbol}")
        self.save()
        return self.invite_code

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.invite_code == None:
            self.generateInvite()
        
        if self.market_cap == None:
            self.market_cap = -1
        
        if self.market_cap != -1:
            if self.initial_balance != 0:
                self.initial_balance = 0
        
        if self.initial_balance == None:
            if self.market_cap != -1:
                self.initial_balance = 0
        
        if self.admin.wallets.filter(currency=self).count() == 0:
            wallet = Wallet(user=self.admin, currency=self, balance=0)
            wallet.save()
            self.admin.wallets.add(wallet)
        
        super().save(*args, **kwargs)

    def get_users(self):
        return self.wallets.all().values_list('user', flat=True)

    def validate_invite(self):
        signer = Signer()
        return self.invite_code == signer.unsign(self.invite_code)

    def validate_cap(self):
        total = self.wallets.all().aggregate(
            models.Sum('balance'))['balance__sum']
        return self.market_cap == -1 or total == None or total <= self.market_cap
    
    def get_admin_wallet(self):
        return self.admin.wallets.filter(currency=self).first()


class Wallet(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wallets')
    balance = models.IntegerField(default=0)
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='wallets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    publickey = models.TextField(max_length=5000, blank=True, null=True)
    privatekey = models.TextField(max_length=5000, blank=True, null=True)

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

    def validate_amount(self):
        amount_earn = self.received.all().aggregate(
            models.Sum('amount'))['amount__sum']
        amount_spend = self.sent.all().aggregate(
            models.Sum('amount'))['amount__sum']
        return amount_earn - amount_spend == self.balance

    def generateKey(self):
        keyPair = RSA.generate(2048)
        self.publickey = keyPair.publickey().export_key().decode('ascii')
        self.privatekey = keyPair.export_key().decode('ascii')
        self.save()
        return keyPair
    
    def save(self, *args, **kwargs):
        if not self.publickey or not self.privatekey:
            self.generateKey()
        super().save(*args, **kwargs)
    
    # def create(self, user, currency):
    #     self.user = user
    #     self.currency = currency
    #     self.save()
    #     return self
    
    def get_publickey(self):
        return self.publickey

    def get_privatekey(self):
        return self.privatekey
    
    def sign(self, message):
        hash = SHA256.new(message.encode('utf-8'))
        signer = PKCS115_SigScheme(RSA.import_key(self.privatekey))
        signature = signer.sign(hash)
        return binascii.hexlify(signature).decode('ascii')

class Transaction(models.Model):
    sender = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='sent')
    receiver = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='received')
    amount = models.IntegerField()
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    sender_signature = models.TextField(max_length=5000, blank=True, null=True)
    receiver_signature = models.TextField(max_length=5000, blank=True, null=True)


    before_sender_amount_snapshot = models.IntegerField(default=0)
    before_receiver_amount_snapshot = models.IntegerField(default=0)
    after_sender_amount_snapshot = models.IntegerField(default=0)
    after_receiver_amount_snapshot = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.sender.user.username} sent {self.amount} to {self.receiver.user.username}'

    
    def validate_signature(self):
        verifier = PKCS115_SigScheme(RSA.import_key(self.receiver.publickey))
        hash = SHA256.new(f"{self.sender.user.username} sent {self.amount} to {self.receiver.user.username}".encode('utf-8'))
        return verifier.verify(hash, binascii.unhexlify(self.sender_signature))

    def create(self, sender, receiver, amount, currency):
        if sender.currency == currency and receiver.currency == currency:
            if sender.balance >= amount:
                self.sender = sender
                self.receiver = receiver
                self.amount = amount
                self.currency = currency
                self.save()
                return self
            return None
        else:
            return None
    
    def save(self,*args, **kwargs):
        if self.sender.currency == self.currency and self.receiver.currency == self.currency:
            self.before_sender_amount_snapshot = self.sender.balance
            self.before_receiver_amount_snapshot = self.receiver.balance
            self.sender_signature = self.sender.sign(f"{self.sender.user.username} sent {self.amount} to {self.receiver.user.username}")
            self.receiver_signature = self.receiver.sign(f"{self.sender.user.username} sent {self.amount} to {self.receiver.user.username}")
            super().save(*args, **kwargs)
            if self.sender.balance >= self.amount:
                self.sender.withdraw(self.amount)
                self.receiver.deposit(self.amount)
                self.after_sender_amount_snapshot = self.sender.balance
                self.after_receiver_amount_snapshot = self.receiver.balance
                super().save(*args, **kwargs)

    def validate_currency(self):
        return self.sender.currency == self.currency and self.receiver.currency == self.currency

    def validate_amount(self):
        return self.sender_amount_snapshot - self.amount == self.after_sender_amount_snapshot and self.receiver_amount_snapshot + self.amount == self.after_receiver_amount_snapshot
