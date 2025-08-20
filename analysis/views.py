from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ThreatAssessment, TrendAnalysis, Alert, AutoAnalysisRule
from intelligence.models import IntelligenceReport
from .serializers import ThreatAssessmentSerializer, TrendAnalysisSerializer, AlertSerializer

class AnalysisHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'analysis/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques d'analyse
        context['stats'] = {
            'total_assessments': ThreatAssessment.objects.count(),
            'pending_assessments': ThreatAssessment.objects.filter(status='DRAFT').count(),
            'active_alerts': Alert.objects.filter(is_active=True).count(),
            'trend_analyses': TrendAnalysis.objects.count(),
        }
        
        # Évaluations récentes
        context['recent_assessments'] = ThreatAssessment.objects.select_related(
            'analyst'
        ).order_by('-created_at')[:5]
        
        # Alertes actives récentes
        context['recent_alerts'] = Alert.objects.filter(
            is_active=True
        ).select_related('created_by').order_by('-created_at')[:5]
        
        return context

class ThreatAssessmentListView(LoginRequiredMixin, ListView):
    model = ThreatAssessment
    template_name = 'analysis/assessment_list.html'
    context_object_name = 'assessments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ThreatAssessment.objects.select_related('analyst', 'reviewed_by')
        
        # Filtres
        status_filter = self.request.GET.get('status')
        assessment_type_filter = self.request.GET.get('assessment_type')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if assessment_type_filter:
            queryset = queryset.filter(assessment_type=assessment_type_filter)
        
        return queryset.order_by('-created_at')

class ThreatAssessmentDetailView(LoginRequiredMixin, DetailView):
    model = ThreatAssessment
    template_name = 'analysis/assessment_detail.html'
    context_object_name = 'assessment'

class ThreatAssessmentCreateView(LoginRequiredMixin, CreateView):
    model = ThreatAssessment
    template_name = 'analysis/assessment_form.html'
    fields = [
        'title', 'assessment_type', 'executive_summary', 'detailed_analysis',
        'key_findings', 'recommendations', 'probability_score', 'impact_score',
        'classification_level', 'valid_from', 'valid_until'
    ]
    
    def form_valid(self, form):
        form.instance.analyst = self.request.user
        return super().form_valid(form)

class TrendAnalysisListView(LoginRequiredMixin, ListView):
    model = TrendAnalysis
    template_name = 'analysis/trend_list.html'
    context_object_name = 'trends'
    paginate_by = 20
    
    def get_queryset(self):
        return TrendAnalysis.objects.select_related('analyst').order_by('-created_at')

class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = 'analysis/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Alert.objects.select_related('created_by')
        
        # Filtrer par statut actif par défaut
        active_only = self.request.GET.get('active_only', 'true')
        if active_only.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        # Filtre par niveau d'alerte
        alert_level = self.request.GET.get('alert_level')
        if alert_level:
            queryset = queryset.filter(alert_level=alert_level)
        
        return queryset.order_by('-created_at')

# API ViewSets
class ThreatAssessmentViewSet(viewsets.ModelViewSet):
    serializer_class = ThreatAssessmentSerializer
    
    def get_queryset(self):
        return ThreatAssessment.objects.select_related('analyst', 'reviewed_by')
    
    def perform_create(self, serializer):
        serializer.save(analyst=self.request.user)

class TrendAnalysisViewSet(viewsets.ModelViewSet):
    serializer_class = TrendAnalysisSerializer
    
    def get_queryset(self):
        return TrendAnalysis.objects.select_related('analyst')
    
    def perform_create(self, serializer):
        serializer.save(analyst=self.request.user)

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    
    def get_queryset(self):
        queryset = Alert.objects.select_related('created_by')
        
        # Filtrer par utilisateur si demandé
        user_only = self.request.query_params.get('user_only', 'false')
        if user_only.lower() == 'true':
            queryset = queryset.filter(
                Q(target_users=self.request.user) |
                Q(target_roles__contains=self.request.user.rank)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@api_view(['POST'])
@login_required
def analyze_report(request, report_id):
    """Analyse automatique d'un rapport"""
    try:
        report = IntelligenceReport.objects.get(id=report_id)
        
        # Analyser selon les règles automatiques
        rules = AutoAnalysisRule.objects.filter(is_active=True).order_by('priority')
        
        analysis_results = {
            'report_id': str(report_id),
            'threat_level_recommendation': None,
            'suggested_categories': [],
            'risk_indicators': [],
            'confidence_score': 0,
        }
        
        # Application des règles d'analyse
        for rule in rules:
            if evaluate_rule_conditions(rule, report):
                execute_rule_actions(rule, report, analysis_results)
                
                # Mettre à jour les statistiques de la règle
                rule.execution_count += 1
                rule.last_executed = timezone.now()
                rule.save()
        
        return Response(analysis_results)
    
    except IntelligenceReport.DoesNotExist:
        return Response({'error': 'Rapport non trouvé'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@login_required
def generate_alert(request):
    """Génère une alerte basée sur les critères fournis"""
    try:
        data = request.data
        
        alert = Alert.objects.create(
            title=data.get('title'),
            message=data.get('message'),
            alert_level=data.get('alert_level', 'INFO'),
            alert_type=data.get('alert_type', 'SYSTEM_ALERT'),
            created_by=request.user
        )
        
        # Ajouter les utilisateurs cibles
        target_user_ids = data.get('target_users', [])
        if target_user_ids:
            alert.target_users.set(target_user_ids)
        
        # Ajouter les rôles cibles
        target_roles = data.get('target_roles', [])
        if target_roles:
            alert.target_roles = target_roles
            alert.save()
        
        serializer = AlertSerializer(alert)
        return Response(serializer.data, status=201)
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def evaluate_rule_conditions(rule, report):
    """Évalue si les conditions d'une règle sont remplies"""
    conditions = rule.trigger_conditions
    
    # Évaluation simple des conditions (à étendre selon les besoins)
    if 'threat_level' in conditions:
        if report.threat_level not in conditions['threat_level']:
            return False
    
    if 'keywords' in conditions:
        keywords = conditions['keywords']
        text_to_search = f"{report.title} {report.description}".lower()
        if not any(keyword.lower() in text_to_search for keyword in keywords):
            return False
    
    if 'confidence_threshold' in conditions:
        if report.confidence_level < conditions['confidence_threshold']:
            return False
    
    return True

def execute_rule_actions(rule, report, analysis_results):
    """Exécute les actions définies dans une règle"""
    actions = rule.actions
    
    if 'set_threat_level' in actions:
        analysis_results['threat_level_recommendation'] = actions['set_threat_level']
    
    if 'add_categories' in actions:
        analysis_results['suggested_categories'].extend(actions['add_categories'])
    
    if 'add_risk_indicators' in actions:
        analysis_results['risk_indicators'].extend(actions['add_risk_indicators'])
    
    if 'confidence_modifier' in actions:
        modifier = actions['confidence_modifier']
        analysis_results['confidence_score'] += modifier
    
    if 'create_alert' in actions:
        alert_config = actions['create_alert']
        Alert.objects.create(
            title=alert_config.get('title', f'Alerte automatique - {report.title}'),
            message=alert_config.get('message', f'Rapport {report.title} déclenche une alerte'),
            alert_level=alert_config.get('level', 'WARNING'),
            alert_type='PATTERN_DETECTED',
            triggered_by_report=report,
            created_by_id=1  # Système
        )