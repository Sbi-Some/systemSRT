from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from intelligence.models import IntelligenceReport, ThreatCategory, HostileGroup

User = get_user_model()

class ThreatAssessment(models.Model):
    ASSESSMENT_TYPES = [
        ('IMMEDIATE', 'Immédiate'),
        ('SHORT_TERM', 'Court terme'),
        ('MEDIUM_TERM', 'Moyen terme'),
        ('LONG_TERM', 'Long terme'),
        ('STRATEGIC', 'Stratégique'),
    ]
    
    title = models.CharField(max_length=255)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    threat_categories = models.ManyToManyField(ThreatCategory)
    hostile_groups = models.ManyToManyField(HostileGroup, blank=True)
    related_reports = models.ManyToManyField(IntelligenceReport)
    
    executive_summary = models.TextField()
    detailed_analysis = models.TextField()
    key_findings = models.JSONField(default=list)
    recommendations = models.TextField()
    
    probability_score = models.IntegerField(
        help_text="Probabilité (1-100%)",
        validators=[models.validators.MinValueValidator(1), models.validators.MaxValueValidator(100)]
    )
    impact_score = models.IntegerField(
        help_text="Impact (1-100)",
        validators=[models.validators.MinValueValidator(1), models.validators.MaxValueValidator(100)]
    )
    
    analyst = models.ForeignKey(User, on_delete=models.PROTECT, related_name='threat_assessments')
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_assessments'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('DRAFT', 'Brouillon'),
            ('UNDER_REVIEW', 'En révision'),
            ('APPROVED', 'Approuvé'),
            ('PUBLISHED', 'Publié'),
            ('ARCHIVED', 'Archivé'),
        ],
        default='DRAFT'
    )
    
    classification_level = models.CharField(
        max_length=20,
        choices=[
            ('RESTRICTED', 'Restreint'),
            ('CONFIDENTIAL', 'Confidentiel'),
            ('SECRET', 'Secret'),
            ('TOP_SECRET', 'Très Secret'),
        ],
        default='RESTRICTED'
    )
    
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Évaluation de Menace'
        verbose_name_plural = 'Évaluations de Menaces'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def get_risk_score(self):
        """Calcule le score de risque basé sur probabilité et impact"""
        return (self.probability_score * self.impact_score) / 100

class TrendAnalysis(models.Model):
    TREND_TYPES = [
        ('THREAT_EVOLUTION', 'Évolution des Menaces'),
        ('GEOGRAPHIC_PATTERN', 'Motifs Géographiques'),
        ('TEMPORAL_PATTERN', 'Motifs Temporels'),
        ('SOURCE_RELIABILITY', 'Fiabilité des Sources'),
        ('ACTIVITY_INCREASE', 'Augmentation d\'Activité'),
        ('ACTIVITY_DECREASE', 'Diminution d\'Activité'),
    ]
    
    title = models.CharField(max_length=255)
    trend_type = models.CharField(max_length=30, choices=TREND_TYPES)
    description = models.TextField()
    
    analyzed_reports = models.ManyToManyField(IntelligenceReport)
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    
    key_metrics = models.JSONField(default=dict)
    visualization_data = models.JSONField(default=dict)
    confidence_level = models.IntegerField(
        validators=[models.validators.MinValueValidator(1), models.validators.MaxValueValidator(100)]
    )
    
    analyst = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Analyse de Tendance'
        verbose_name_plural = 'Analyses de Tendances'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_trend_type_display()})"

class Alert(models.Model):
    ALERT_LEVELS = [
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('CRITICAL', 'Critique'),
        ('EMERGENCY', 'Urgence'),
    ]
    
    ALERT_TYPES = [
        ('THREAT_ESCALATION', 'Escalade de Menace'),
        ('NEW_INTELLIGENCE', 'Nouveau Renseignement'),
        ('PATTERN_DETECTED', 'Motif Détecté'),
        ('DEADLINE_APPROACHING', 'Échéance Approchante'),
        ('SYSTEM_ALERT', 'Alerte Système'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVELS)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    
    triggered_by_report = models.ForeignKey(
        IntelligenceReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    triggered_by_assessment = models.ForeignKey(
        ThreatAssessment,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    target_users = models.ManyToManyField(User, related_name='received_alerts')
    target_roles = models.JSONField(default=list, blank=True)
    
    is_active = models.BooleanField(default=True)
    auto_expire = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_alerts')
    
    class Meta:
        verbose_name = 'Alerte'
        verbose_name_plural = 'Alertes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_alert_level_display()}"

class AlertAcknowledgment(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='acknowledgments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Accusé de Réception'
        verbose_name_plural = 'Accusés de Réception'
        unique_together = ('alert', 'user')
    
    def __str__(self):
        return f"AR - {self.alert.title} - {self.user.get_full_name()}"

class AutoAnalysisRule(models.Model):
    """Règles pour l'analyse automatique des rapports"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    # Conditions de déclenchement
    trigger_conditions = models.JSONField(help_text="Conditions JSON pour déclencher la règle")
    
    # Actions à effectuer
    actions = models.JSONField(help_text="Actions JSON à effectuer quand la règle est déclenchée")
    
    priority = models.IntegerField(default=100)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statistiques d'utilisation
    execution_count = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Règle d\'Analyse Auto'
        verbose_name_plural = 'Règles d\'Analyse Auto'
        ordering = ['priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({'Actif' if self.is_active else 'Inactif'})"