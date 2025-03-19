from django.db import models

import random
import string

def generate_user_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits , k=length))

class User(models.Model) :
    user_id = models.CharField(max_length=8, unique=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    frist_name = models.CharField(max_length=44)
    last_name = models.CharField(max_length=44)
    email =models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15 , unique=True)
    profile_picture = models.ImageField(upload_to='profiles/' , blank=True , null=True)
    dob = models.DateField()
    bio = models.TextField(blank=True , null=True)
    password = models.CharField(max_length=25)

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = generate_user_id()
        super().save(*args , **kwargs)

    def __str__(self):
        return self.username