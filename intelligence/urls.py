from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'intelligence'

# API Routes
router = DefaultRouter()
router.register(r'reports', views.IntelligenceReportViewSet)
router.register(r'threat-categories', views.ThreatCategoryViewSet)
router.register(r'hostile-groups', views.HostileGroupViewSet)
router.register(r'geographic-zones', views.GeographicZoneViewSet)

urlpatterns = [
    # Web views
    path('', views.IntelligenceHomeView.as_view(), name='home'),
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/new/', views.ReportCreateView.as_view(), name='report_create'),
    path('reports/<uuid:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('reports/<uuid:pk>/edit/', views.ReportUpdateView.as_view(), name='report_edit'),
    path('map/', views.IntelligenceMapView.as_view(), name='map'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('groups/', views.HostileGroupListView.as_view(), name='group_list'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/upload-attachment/', views.upload_attachment, name='upload_attachment'),
    path('api/map-data/', views.map_data, name='map_data'),
]