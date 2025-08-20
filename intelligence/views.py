from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

from .models import (
    IntelligenceReport, ThreatCategory, HostileGroup, 
    GeographicZone, ReportAttachment
)
from .serializers import (
    IntelligenceReportSerializer, ThreatCategorySerializer,
    HostileGroupSerializer, GeographicZoneSerializer
)
from .forms import IntelligenceReportForm

class IntelligenceHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'intelligence/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques récentes
        context['stats'] = {
            'total_reports': IntelligenceReport.objects.count(),
            'new_reports': IntelligenceReport.objects.filter(status='NEW').count(),
            'critical_reports': IntelligenceReport.objects.filter(threat_level='CRITICAL').count(),
            'threat_categories': ThreatCategory.objects.filter(is_active=True).count(),
        }
        
        # Rapports récents par niveau de menace
        context['reports_by_threat'] = {
            'critical': IntelligenceReport.objects.filter(threat_level='CRITICAL').order_by('-created_at')[:3],
            'high': IntelligenceReport.objects.filter(threat_level='HIGH').order_by('-created_at')[:3],
        }
        
        return context

class ReportListView(LoginRequiredMixin, ListView):
    model = IntelligenceReport
    template_name = 'intelligence/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = IntelligenceReport.objects.select_related(
            'source_agent', 'assigned_analyst'
        ).prefetch_related('threat_categories', 'hostile_groups')
        
        # Filtres
        status_filter = self.request.GET.get('status')
        threat_filter = self.request.GET.get('threat_level')
        category_filter = self.request.GET.get('category')
        search = self.request.GET.get('search')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if threat_filter:
            queryset = queryset.filter(threat_level=threat_filter)
        
        if category_filter:
            queryset = queryset.filter(threat_categories__id=category_filter)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location_description__icontains=search)
            )
        
        return queryset.order_by('-report_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['threat_categories'] = ThreatCategory.objects.filter(is_active=True)
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'threat_level': self.request.GET.get('threat_level', ''),
            'category': self.request.GET.get('category', ''),
            'search': self.request.GET.get('search', ''),
        }
        return context

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = IntelligenceReport
    template_name = 'intelligence/report_detail.html'
    context_object_name = 'report'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachments'] = self.object.attachment_files.all()
        context['comments'] = self.object.comments.all().order_by('-created_at')
        context['related_reports'] = self.object.related_reports.all()[:5]
        return context

class ReportCreateView(LoginRequiredMixin, CreateView):
    model = IntelligenceReport
    form_class = IntelligenceReportForm
    template_name = 'intelligence/report_form.html'
    
    def form_valid(self, form):
        form.instance.source_agent = self.request.user
        messages.success(self.request, 'Rapport créé avec succès!')
        return super().form_valid(form)

class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = IntelligenceReport
    form_class = IntelligenceReportForm
    template_name = 'intelligence/report_form.html'
    
    def form_valid(self, form):
        form.instance.version += 1
        messages.success(self.request, 'Rapport mis à jour avec succès!')
        return super().form_valid(form)

class IntelligenceMapView(LoginRequiredMixin, TemplateView):
    template_name = 'intelligence/map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['threat_categories'] = ThreatCategory.objects.filter(is_active=True)
        context['geographic_zones'] = GeographicZone.objects.filter(is_monitored=True)
        return context

class CategoryListView(LoginRequiredMixin, ListView):
    model = ThreatCategory
    template_name = 'intelligence/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return ThreatCategory.objects.filter(is_active=True).annotate(
            report_count=Count('intelligencereport')
        ).order_by('category_type', 'name')

class HostileGroupListView(LoginRequiredMixin, ListView):
    model = HostileGroup
    template_name = 'intelligence/group_list.html'
    context_object_name = 'groups'
    
    def get_queryset(self):
        return HostileGroup.objects.prefetch_related('threat_categories').order_by('name')

# API ViewSets
class IntelligenceReportViewSet(viewsets.ModelViewSet):
    serializer_class = IntelligenceReportSerializer
    
    def get_queryset(self):
        queryset = IntelligenceReport.objects.all()
        
        # Filtres via paramètres URL
        status = self.request.query_params.get('status', None)
        threat_level = self.request.query_params.get('threat_level', None)
        
        if status:
            queryset = queryset.filter(status=status)
        if threat_level:
            queryset = queryset.filter(threat_level=threat_level)
        
        return queryset.order_by('-created_at')

class ThreatCategoryViewSet(viewsets.ModelViewSet):
    queryset = ThreatCategory.objects.filter(is_active=True)
    serializer_class = ThreatCategorySerializer

class HostileGroupViewSet(viewsets.ModelViewSet):
    queryset = HostileGroup.objects.all()
    serializer_class = HostileGroupSerializer

class GeographicZoneViewSet(viewsets.ModelViewSet):
    queryset = GeographicZone.objects.filter(is_monitored=True)
    serializer_class = GeographicZoneSerializer

@api_view(['POST'])
@login_required
def upload_attachment(request):
    """API pour l'upload de pièces jointes"""
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        file = request.FILES.get('file')
        description = request.POST.get('description', '')
        
        if not report_id or not file:
            return JsonResponse({'error': 'Report ID et fichier requis'}, status=400)
        
        try:
            report = IntelligenceReport.objects.get(id=report_id)
            
            # Déterminer le type de fichier
            file_type = 'DOCUMENT'
            if file.content_type.startswith('image/'):
                file_type = 'IMAGE'
            elif file.content_type.startswith('video/'):
                file_type = 'VIDEO'
            elif file.content_type.startswith('audio/'):
                file_type = 'AUDIO'
            
            attachment = ReportAttachment.objects.create(
                report=report,
                file=file,
                file_type=file_type,
                filename=file.name,
                file_size=file.size,
                description=description,
                uploaded_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'attachment': {
                    'id': attachment.id,
                    'filename': attachment.filename,
                    'file_type': attachment.get_file_type_display(),
                    'file_size': attachment.file_size,
                    'url': attachment.file.url
                }
            })
        
        except IntelligenceReport.DoesNotExist:
            return JsonResponse({'error': 'Rapport non trouvé'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@api_view(['GET'])
def map_data(request):
    """API pour les données de la carte"""
    reports = IntelligenceReport.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('source_agent')
    
    # Filtres optionnels
    threat_level = request.GET.get('threat_level')
    days = request.GET.get('days', 30)
    
    if threat_level:
        reports = reports.filter(threat_level=threat_level)
    
    try:
        days = int(days)
        from django.utils import timezone
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        reports = reports.filter(created_at__gte=cutoff_date)
    except ValueError:
        pass
    
    # Formater les données pour la carte
    map_reports = []
    for report in reports[:100]:  # Limiter à 100 points
        map_reports.append({
            'id': str(report.id),
            'title': report.title,
            'latitude': float(report.latitude),
            'longitude': float(report.longitude),
            'threat_level': report.threat_level,
            'report_date': report.report_date.strftime('%Y-%m-%d %H:%M'),
            'location_description': report.location_description,
            'agent': report.source_agent.get_full_name(),
        })
    
    # Zones géographiques
    zones = []
    for zone in GeographicZone.objects.filter(is_monitored=True):
        zones.append({
            'id': zone.id,
            'name': zone.name,
            'zone_type': zone.zone_type,
            'risk_level': zone.risk_level,
            'coordinates': zone.coordinates,
        })
    
    return JsonResponse({
        'reports': map_reports,
        'zones': zones,
    })