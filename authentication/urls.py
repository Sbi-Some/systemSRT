from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.SecureLoginView.as_view(), name='login'),
    path('logout/', views.SecureLogoutView.as_view(), name='logout'),
    path('password-change/', views.SecurePasswordChangeView.as_view(), name='password_change'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('security-events/', views.SecurityEventsView.as_view(), name='security_events'),
]