from django.urls import path
from .views import UserRegistrationView, PasswordResetRequestView, PasswordResetVerifyView, PasswordResetConfirmView, LogoutView, CustomTokenObtainPairView, EventoListView, AlertaListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', PasswordResetVerifyView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('events/', EventoListView.as_view(), name='event-list'),
    path('alerts/', AlertaListView.as_view(), name='alert-list'),
]