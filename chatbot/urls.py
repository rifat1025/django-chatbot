from django.urls import path
from .views import DocumentUploadAPIView,ChatAPIView
urlpatterns = [
    path('documents/', DocumentUploadAPIView.as_view(), name='document-upload'),
    path('chat/', ChatAPIView.as_view(), name='chat'),

    
]