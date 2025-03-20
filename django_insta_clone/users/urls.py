from django.urls import path

from .views import *
from  . import views

urlpatterns = [
     path('register/' , register  , name = "register"),
     path('login/' , login  , name = "login"),
     path('profile/' , views.get_profile , name = 'profile'),
]