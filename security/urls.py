from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('dashboard/', views.SecurityDashboardView.as_view(), name='dashboard'),
    path('events/', views.SecurityEventsView.as_view(), name='events'),
    path('api/metrics/', views.security_metrics, name='metrics'),
    path('api/status/', views.system_status, name='status'),
]