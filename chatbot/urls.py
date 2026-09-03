from django.urls import path
from .views import DocumentUploadAPIView
urlpatterns = [
    path('documents/', DocumentUploadAPIView.as_view(), name='document-upload'),
    
]