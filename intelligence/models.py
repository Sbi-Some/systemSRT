from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()

class ThreatCategory(models.Model):
    CATEGORY_TYPES = [
        ('TERRORIST', 'Terroriste'),
        ('CRIMINAL', 'Criminelle'),
        ('CYBER', 'Cybermenace'),
        ('ESPIONAGE', 'Espionnage'),
        ('SABOTAGE', 'Sabotage'),
        ('TRAFFICKING', 'Trafic'),
        ('OTHER', 'Autre'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#ff0000')  # Hex color
    priority_weight = models.IntegerField(
        default=1, 
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Catégorie de Menace'
        verbose_name_plural = 'Catégories de Menaces'
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

class HostileGroup(models.Model):
    name = models.CharField(max_length=200, unique=True)
    aliases = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    threat_categories = models.ManyToManyField(ThreatCategory, related_name='hostile_groups')
    estimated_members = models.IntegerField(null=True, blank=True)
    leadership = models.TextField(blank=True)
    known_locations = models.JSONField(default=list, blank=True)
    activity_status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Actif'),
            ('INACTIVE', 'Inactif'),
            ('DISBANDED', 'Dissous'),
            ('UNKNOWN', 'Inconnu'),
        ],
        default='UNKNOWN'
    )
    threat_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Faible'),
            ('MEDIUM', 'Moyen'),
            ('HIGH', 'Élevé'),
            ('CRITICAL', 'Critique'),
        ],
        default='MEDIUM'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Groupe Hostile'
        verbose_name_plural = 'Groupes Hostiles'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class IntelligenceReport(models.Model):
    REPORT_TYPES = [
        ('HUMINT', 'Renseignement Humain'),
        ('SIGINT', 'Renseignement Électronique'),
        ('IMINT', 'Renseignement Imagerie'),
        ('OSINT', 'Renseignement Source Ouverte'),
        ('TECHINT', 'Renseignement Technique'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'Nouveau'),
        ('IN_PROGRESS', 'En Cours'),
        ('ANALYZED', 'Analysé'),
        ('VERIFIED', 'Vérifié'),
        ('ARCHIVED', 'Archivé'),
        ('REJECTED', 'Rejeté'),
    ]
    
    CLASSIFICATION_LEVELS = [
        ('PUBLIC', 'Public'),
        ('RESTRICTED', 'Restreint'),
        ('CONFIDENTIAL', 'Confidentiel'),
        ('SECRET', 'Secret'),
        ('TOP_SECRET', 'Très Secret'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    classification_level = models.CharField(
        max_length=20, 
        choices=CLASSIFICATION_LEVELS, 
        default='RESTRICTED'
    )
    
    # Source information
    source_agent = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='submitted_reports'
    )
    source_type = models.CharField(
        max_length=20,
        choices=[
            ('FIELD_AGENT', 'Agent de Terrain'),
            ('ELECTRONIC', 'Électronique'),
            ('INFORMANT', 'Informateur'),
            ('SURVEILLANCE', 'Surveillance'),
            ('INTERCEPTED', 'Intercepté'),
        ]
    )
    
    # Location information
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_description = models.CharField(max_length=255, blank=True)
    
    # Threat analysis
    threat_categories = models.ManyToManyField(ThreatCategory, blank=True)
    hostile_groups = models.ManyToManyField(HostileGroup, blank=True)
    threat_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Faible'),
            ('MEDIUM', 'Moyen'),
            ('HIGH', 'Élevé'),
            ('CRITICAL', 'Critique'),
        ],
        default='MEDIUM'
    )
    confidence_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Niveau de confiance (1-100%)"
    )
    
    # Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    assigned_analyst = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_reports'
    )
    priority = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Priorité (1=Très Haute, 5=Très Basse)"
    )
    
    # Attachments and evidence
    attachments = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Timestamps
    report_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    version = models.IntegerField(default=1)
    related_reports = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    class Meta:
        verbose_name = 'Rapport de Renseignement'
        verbose_name_plural = 'Rapports de Renseignement'
        ordering = ['-report_date', '-priority']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['threat_level', 'report_date']),
            models.Index(fields=['classification_level']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def get_location_display(self):
        if self.location_description:
            return self.location_description
        elif self.latitude and self.longitude:
            return f"Lat: {self.latitude:.4f}, Lon: {self.longitude:.4f}"
        return "Localisation non spécifiée"

class ReportAttachment(models.Model):
    ATTACHMENT_TYPES = [
        ('IMAGE', 'Image'),
        ('DOCUMENT', 'Document'),
        ('VIDEO', 'Vidéo'),
        ('AUDIO', 'Audio'),
        ('DATA', 'Données'),
    ]
    
    report = models.ForeignKey(
        IntelligenceReport, 
        on_delete=models.CASCADE, 
        related_name='attachment_files'
    )
    file = models.FileField(upload_to='intelligence/attachments/%Y/%m/')
    file_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    description = models.TextField(blank=True)
    is_evidence = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Pièce Jointe'
        verbose_name_plural = 'Pièces Jointes'
    
    def __str__(self):
        return f"{self.filename} - {self.report.title}"

class ReportComment(models.Model):
    report = models.ForeignKey(
        IntelligenceReport,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    content = models.TextField()
    is_internal = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commentaire de {self.author.get_full_name()} - {self.created_at}"

class GeographicZone(models.Model):
    ZONE_TYPES = [
        ('CITY', 'Ville'),
        ('REGION', 'Région'),
        ('BORDER', 'Frontière'),
        ('FACILITY', 'Installation'),
        ('ROUTE', 'Route/Axe'),
        ('AREA', 'Zone'),
    ]
    
    name = models.CharField(max_length=200)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPES)
    description = models.TextField(blank=True)
    coordinates = models.JSONField(help_text="Coordonnées GeoJSON")
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('LOW', 'Faible'),
            ('MEDIUM', 'Moyen'),
            ('HIGH', 'Élevé'),
            ('CRITICAL', 'Critique'),
        ],
        default='MEDIUM'
    )
    is_monitored = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Zone Géographique'
        verbose_name_plural = 'Zones Géographiques'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"