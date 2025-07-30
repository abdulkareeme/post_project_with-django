from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from .models import CustomUser as User

# Register with Generic
class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self,request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        token = AuthToken.objects.create(user)[1]
        return Response({
            "user" : UserSerializer(user).data ,
            "token" : token
       })
# Login with ApiView
class LoginAPIView(APIView) :
    def post(self , request , *args , **kwargs):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token = AuthToken.objects.create(user)[1]
        return Response({
            'user' : UserSerializer(user).data ,
            'token' : token
        })

# display all users in database with ViewSet
class ListOfUser(viewsets.ViewSet):
    def list(self , request):
        users = User.objects.all()
        data = UserSerializer(users , many=True).data
        return Response(data)

