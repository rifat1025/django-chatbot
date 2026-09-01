from django.urls import path
from .views import Chatbot 

urlpatterns = [
    path('/',views.Chatbot)
]
