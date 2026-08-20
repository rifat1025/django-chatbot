from django.urls import path
from .views import User_lists

urlpatterns = [
    
    path("users/",User_lists.as_view(),name='users')
]
