from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'analysis'

# API Routes
router = DefaultRouter()
router.register(r'threat-assessments', views.ThreatAssessmentViewSet)
router.register(r'trend-analyses', views.TrendAnalysisViewSet)
router.register(r'alerts', views.AlertViewSet)

urlpatterns = [
    # Web views
    path('', views.AnalysisHomeView.as_view(), name='home'),
    path('threat-assessments/', views.ThreatAssessmentListView.as_view(), name='assessment_list'),
    path('threat-assessments/new/', views.ThreatAssessmentCreateView.as_view(), name='assessment_create'),
    path('threat-assessments/<int:pk>/', views.ThreatAssessmentDetailView.as_view(), name='assessment_detail'),
    path('trends/', views.TrendAnalysisListView.as_view(), name='trend_list'),
    path('alerts/', views.AlertListView.as_view(), name='alert_list'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/analyze-report/<uuid:report_id>/', views.analyze_report, name='analyze_report'),
    path('api/generate-alert/', views.generate_alert, name='generate_alert'),
]