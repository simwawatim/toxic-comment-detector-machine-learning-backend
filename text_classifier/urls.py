from django.urls import path
from text_classifier.views.message_views import MessageCreateAPIView, MessageDetailAPIView, MessageListAPIView
from text_classifier.views.user_view import LoggedInUserProfileAPIView, UserListAPIView, UserProfileAPIView, UserRegisterAPIView, UserLoginAPIView, UserUpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [

    path('messages/', MessageListAPIView.as_view(), name='messages_list'),
    path('messages/send/', MessageCreateAPIView.as_view(), name='message_send'),
    path('messages/<uuid:pk>/', MessageDetailAPIView.as_view(), name='message_detail'),
    path('register/', UserRegisterAPIView.as_view(), name='register'),
    path('users/', UserListAPIView.as_view(), name='users_list'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('users/update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('profile/me/', LoggedInUserProfileAPIView.as_view(), name='logged_in_profile'),
    path('profile/<int:user_id>/', UserProfileAPIView.as_view(), name='user_profile'),
    

    

]
