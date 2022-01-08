import rsa


from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    publickey = models.TextField(max_length=5000, blank=True, null=True)
    privatekey = models.TextField(max_length=5000, blank=True, null=True)


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
