from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255,unique=True)  # Povinné
    password = models.CharField(max_length=255)  # Django už zahŕňa šifrovanie hesiel
    username = None
   
    USERNAME_FIELD = 'email' #Definuje, ktoré pole sa použije na autentifikáciu používateľa (v tomto prípade email).
    REQUIRED_FIELDS = []

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images/')

class Test(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    answer = models.BooleanField()