from django.urls import path
from .views import User_lists,Login

urlpatterns = [
    
    path("users/",User_lists.as_view(),name='users'),
    path('login/',Login.as_view(),name='login')
]
