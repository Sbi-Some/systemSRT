from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Dashboard(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    is_public = models.BooleanField(default=False)
    layout_config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tableau de Bord'
        verbose_name_plural = 'Tableaux de Bord'
    
    def __str__(self):
        return self.name

class Widget(models.Model):
    WIDGET_TYPES = [
        ('CHART', 'Graphique'),
        ('TABLE', 'Tableau'),
        ('MAP', 'Carte'),
        ('COUNTER', 'Compteur'),
        ('ALERT_FEED', 'Flux d\'Alertes'),
        ('REPORT_LIST', 'Liste de Rapports'),
        ('THREAT_OVERVIEW', 'Vue d\'Ensemble des Menaces'),
    ]
    
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=200)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=4)
    config = models.JSONField(default=dict)
    is_visible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Widget'
        verbose_name_plural = 'Widgets'
    
    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"

class SystemMetric(models.Model):
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Métrique Système'
        verbose_name_plural = 'Métriques Système'
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.metric_unit}"