from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dashboard'

# API Routes
router = DefaultRouter()
router.register(r'dashboards', views.DashboardViewSet)
router.register(r'widgets', views.WidgetViewSet)

urlpatterns = [
    # Web views
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('create/', views.DashboardCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DashboardDetailView.as_view(), name='detail'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/metrics/', views.get_metrics, name='metrics'),
    path('api/stats/', views.get_stats, name='stats'),
]