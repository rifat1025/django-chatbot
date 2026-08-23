from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password

# for test my apps
def hello(request):
    return HttpResponse("Test Successfully")

#get user by apiview

# @api_view(['GET'])
# def user_list(request):
#     users = User.objects.all()
#     serializer=UserSerializer(users,many=True)

#     return Response(serializer.data)


# using APIView to retrieve all users 
class User_lists(APIView):

    def get(self,request):
        users  = User.objects.all()
        serializer = UserSerializer(users,many=True)
        return Response (serializer.data)

    def post(self,request):
        # get data from userform
        name = request.data.get('name')

        # condition match the same name 
        if User.objects.filter(name = name ).exists():
            return Response(
            {"error": "Name already exists"},
            status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED

            )
        else:
            return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )


# Login endpoint

class Login(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.MultipleObjectsReturned:
            return Response(
                {"error": "Multiple users have this email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(password, user.password):
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(
            {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            },
            status=status.HTTP_200_OK
        )





