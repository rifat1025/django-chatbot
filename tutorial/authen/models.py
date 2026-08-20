from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=128, null=True, blank=True)
    c_password = models.CharField(max_length=128, null=True, blank=True)