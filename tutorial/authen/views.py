from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User
from .serializers import UserSerializer
from rest_framework.views import APIView

# for test my apps
def hello(request):
    return HttpResponse("Test Successfully")

#get user by apiview

@api_view(['GET'])
def user_list(request):
    users = User.objects.all()
    serializer=UserSerializer(users,many=True)

    return Response(serializer.data)






