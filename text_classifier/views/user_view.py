from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from text_classifier.models import Profile
from text_classifier.serializers.users.serializers import UserRegisterSerializer
from utils.decorators import jwt_required
from utils.response import api_response
from rest_framework import status


class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return api_response(
                status_code=status.HTTP_201_CREATED,
                status='success',
                message='User registered successfully',
                data={'username': user.username, 'email': user.email}
            )
        return api_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            status='fail',
            data=serializer.errors,
            is_error=True
        )

class UserLoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return api_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                status='fail',
                message='Username and password are required'
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return api_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                status='fail',
                message='Invalid username or password'
            )

        refresh = RefreshToken.for_user(user)
        return api_response(
            status_code=status.HTTP_200_OK,
            status='success',
            message='Login successful',
            data={
                'username': user.username,
                'email': user.email,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        )

class UserListAPIView(APIView):
    authentication_classes = []
    @jwt_required
    def get(self, request):
        users = User.objects.all()
        users_data = []
        for user in users:
            profile = getattr(user, 'profile', None)
            users_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_picture": profile.profile_picture.url if profile and profile.profile_picture else None
            })
        return api_response(
            status_code=status.HTTP_200_OK,
            status='success',
            message='Users retrieved successfully',
            data=users_data
        )


class UserUpdateAPIView(APIView):
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @jwt_required
    def put(self, request):
        user = request.user
        data = request.data
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        if data.get('password'):
            user.set_password(data['password'])
        user.save()

        userProfile, _ = Profile.objects.get_or_create(user=user)

        if 'profile_picture' in request.FILES:
            userProfile.profile_picture = request.FILES['profile_picture']
            userProfile.save()

        return api_response(
            status_code=status.HTTP_200_OK,
            status='success',
            message='User info updated successfully',
            data={
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile_picture': userProfile.profile_picture.url if userProfile.profile_picture else None,
            }
        )


class LoggedInUserProfileAPIView(APIView):
    authentication_classes = []
    
    @jwt_required
    def get(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        return api_response(
            status_code=status.HTTP_200_OK,
            status='success',
            message='Logged-in user profile retrieved',
            data={
                'username': user.username,
                'email': user.email,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
            }
        )

class UserProfileAPIView(APIView):
    authentication_classes = []
    
    @jwt_required
    def get(self, request, user_id=None):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return api_response(
                status_code=status.HTTP_404_NOT_FOUND,
                status='fail',
                message='User not found'
            )

        profile, _ = Profile.objects.get_or_create(user=user)

        return api_response(
            status_code=status.HTTP_200_OK,
            status='success',
            message='User profile retrieved',
            data={
                'username': user.username,
                'email': user.email,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
            }
        )
