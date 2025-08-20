from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from .models import SecurityEvent, SystemHealth, DataClassification
from authentication.models import User, AccessAttempt

class SecurityDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'security/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Vérifier les permissions
        if self.request.user.rank not in ['ADMINISTRATOR', 'DIRECTOR']:
            context['access_denied'] = True
            return context
        
        # Statistiques de sécurité
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        context['security_stats'] = {
            'total_events': SecurityEvent.objects.count(),
            'critical_events': SecurityEvent.objects.filter(
                severity='CRITICAL',
                timestamp__date__gte=week_ago
            ).count(),
            'failed_logins': SecurityEvent.objects.filter(
                event_type='FAILED_LOGIN',
                timestamp__date=today
            ).count(),
            'active_users': User.objects.filter(
                last_activity__date=today
            ).count(),
        }
        
        # Événements récents
        context['recent_events'] = SecurityEvent.objects.order_by('-timestamp')[:10]
        
        # Santé du système
        context['system_health'] = SystemHealth.objects.all()
        
        return context

class SecurityEventsView(LoginRequiredMixin, ListView):
    model = SecurityEvent
    template_name = 'security/events.html'
    context_object_name = 'events'
    paginate_by = 50
    
    def get_queryset(self):
        # Seuls les administrateurs peuvent voir tous les événements
        if self.request.user.rank != 'ADMINISTRATOR':
            return SecurityEvent.objects.filter(user=self.request.user)
        
        queryset = SecurityEvent.objects.all()
        
        # Filtres
        severity = self.request.GET.get('severity')
        event_type = self.request.GET.get('event_type')
        
        if severity:
            queryset = queryset.filter(severity=severity)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        return queryset.order_by('-timestamp')

@login_required
def security_metrics(request):
    """API endpoint pour les métriques de sécurité"""
    if request.user.rank not in ['ADMINISTRATOR', 'DIRECTOR']:
        return JsonResponse({'error': 'Accès refusé'}, status=403)
    
    today = timezone.now().date()
    
    # Métriques des 24 dernières heures
    last_24h = timezone.now() - timedelta(hours=24)
    
    metrics = {
        'login_attempts': AccessAttempt.objects.filter(
            timestamp__gte=last_24h
        ).count(),
        'failed_logins': AccessAttempt.objects.filter(
            timestamp__gte=last_24h,
            success=False
        ).count(),
        'security_events': SecurityEvent.objects.filter(
            timestamp__gte=last_24h
        ).count(),
        'critical_events': SecurityEvent.objects.filter(
            timestamp__gte=last_24h,
            severity='CRITICAL'
        ).count(),
    }
    
    return JsonResponse(metrics)

@login_required
def system_status(request):
    """API endpoint pour le statut du système"""
    if request.user.rank not in ['ADMINISTRATOR', 'DIRECTOR']:
        return JsonResponse({'error': 'Accès refusé'}, status=403)
    
    # Vérifier la santé des composants
    components = SystemHealth.objects.all()
    
    status = {
        'overall_status': 'HEALTHY',
        'components': []
    }
    
    for component in components:
        component_data = {
            'name': component.component_name,
            'status': component.status,
            'response_time': component.response_time,
            'last_check': component.last_check.isoformat() if component.last_check else None
        }
        status['components'].append(component_data)
        
        # Déterminer le statut global
        if component.status in ['CRITICAL', 'DOWN']:
            status['overall_status'] = 'CRITICAL'
        elif component.status == 'WARNING' and status['overall_status'] == 'HEALTHY':
            status['overall_status'] = 'WARNING'
    
    return JsonResponse(status)