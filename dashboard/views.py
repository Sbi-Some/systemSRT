from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta, datetime
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from intelligence.models import IntelligenceReport, ThreatCategory
from analysis.models import Alert, ThreatAssessment
from .models import Dashboard, Widget, SystemMetric
from .serializers import DashboardSerializer, WidgetSerializer

class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['stats'] = self.get_dashboard_stats()
        
        # Recent reports
        context['recent_reports'] = IntelligenceReport.objects.select_related(
            'source_agent'
        ).order_by('-created_at')[:5]
        
        # Active alerts
        context['active_alerts'] = Alert.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        # Chart data
        context['chart_data'] = self.get_chart_data()
        
        context['now'] = timezone.now()
        
        return context
    
    def get_dashboard_stats(self):
        """Calcule les statistiques du tableau de bord"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        stats = {
            'new_reports': IntelligenceReport.objects.filter(
                created_at__date=today
            ).count(),
            
            'critical_threats': IntelligenceReport.objects.filter(
                threat_level='CRITICAL',
                created_at__date__gte=week_ago
            ).count(),
            
            'active_alerts': Alert.objects.filter(
                is_active=True
            ).count(),
            
            'completed_analyses': ThreatAssessment.objects.filter(
                status='APPROVED',
                created_at__date__gte=week_ago
            ).count(),
        }
        
        return stats
    
    def get_chart_data(self):
        """Génère les données pour les graphiques"""
        # Distribution des menaces
        threat_distribution = IntelligenceReport.objects.aggregate(
            critical=Count('id', filter=Q(threat_level='CRITICAL')),
            high=Count('id', filter=Q(threat_level='HIGH')),
            medium=Count('id', filter=Q(threat_level='MEDIUM')),
            low=Count('id', filter=Q(threat_level='LOW'))
        )
        
        # Activité des 7 derniers jours
        activity_labels = []
        activity_data = []
        
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            activity_labels.append(date.strftime('%d/%m'))
            count = IntelligenceReport.objects.filter(
                created_at__date=date
            ).count()
            activity_data.append(count)
        
        activity_labels.reverse()
        activity_data.reverse()
        
        return {
            'threat_distribution': threat_distribution,
            'activity_labels': activity_labels,
            'activity_data': activity_data,
        }

class DashboardCreateView(LoginRequiredMixin, CreateView):
    model = Dashboard
    template_name = 'dashboard/create.html'
    fields = ['name', 'description', 'is_public']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class DashboardDetailView(LoginRequiredMixin, DetailView):
    model = Dashboard
    template_name = 'dashboard/detail.html'
    context_object_name = 'dashboard'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widgets'] = self.object.widgets.filter(is_visible=True).order_by('position_y', 'position_x')
        return context

# API ViewSets
class DashboardViewSet(viewsets.ModelViewSet):
    serializer_class = DashboardSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Dashboard.objects.filter(
            Q(owner=user) | Q(is_public=True)
        )

class WidgetViewSet(viewsets.ModelViewSet):
    serializer_class = WidgetSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Widget.objects.filter(
            dashboard__owner=user
        )

@api_view(['GET'])
def get_metrics(request):
    """API endpoint pour récupérer les métriques système"""
    metrics = {}
    
    # Métriques récentes
    recent_metrics = SystemMetric.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).values('metric_name').annotate(
        latest_value=Count('metric_value')
    )
    
    for metric in recent_metrics:
        metrics[metric['metric_name']] = metric['latest_value']
    
    return Response(metrics)

@api_view(['GET'])
def get_stats(request):
    """API endpoint pour les statistiques en temps réel"""
    today = timezone.now().date()
    
    stats = {
        'new_reports': IntelligenceReport.objects.filter(
            created_at__date=today
        ).count(),
        
        'critical_threats': IntelligenceReport.objects.filter(
            threat_level='CRITICAL',
            created_at__date=today
        ).count(),
        
        'active_alerts': Alert.objects.filter(
            is_active=True
        ).count(),
        
        'completed_analyses': ThreatAssessment.objects.filter(
            status='APPROVED',
            created_at__date=today
        ).count(),
    }
    
    return Response(stats)