from rest_framework import serializers
from .models import CustomUser as User

# i use this serializer to display the information of user after login ,register(in postman)
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['full_name' , 'email' ]

    def get_full_name(self, obj):
            return f"{obj.first_name} {obj.last_name}"
           


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name' , 'last_name' , 'email' , 'password' ]   
        extra_kwargs = {'password': {'write_only': True}}

    # this **validated_data is mean :
    # user = User.Objects.create_user(
    #           username='ahmad',
    #           email='ahmad@example.com',
    #           password='123456')
    def create(self , validated_data):
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")
        email = validated_data.get("email", "").lower()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Something went Wrong."})

        # Generate username
        generated_username = f"{first_name.lower()}_{last_name.lower()}"

        original_username = generated_username
        counter = 1
        while User.objects.filter(username=generated_username).exists():
            generated_username = f"{original_username}{counter}"
            counter += 1

        validated_data["username"] = generated_username

        user = User.objects.create_user(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField() 
    password = serializers.CharField(write_only= True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid login ")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid login ")
        return user