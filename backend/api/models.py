import rsa


from django.db import models
from django.contrib.auth.models import AbstractUser
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
