from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class SecurityEvent(models.Model):
    EVENT_TYPES = [
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('FAILED_LOGIN', 'Échec de connexion'),
        ('PASSWORD_CHANGE', 'Changement mot de passe'),
        ('PERMISSION_DENIED', 'Accès refusé'),
        ('DATA_ACCESS', 'Accès aux données'),
        ('DATA_MODIFICATION', 'Modification données'),
        ('SUSPICIOUS_ACTIVITY', 'Activité suspecte'),
        ('SECURITY_BREACH', 'Violation de sécurité'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyen'),
        ('HIGH', 'Élevé'),
        ('CRITICAL', 'Critique'),
    ]
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    description = models.TextField()
    additional_data = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Investigation
    investigated = models.BooleanField(default=False)
    investigated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigated_events'
    )
    investigation_notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Événement de Sécurité'
        verbose_name_plural = 'Événements de Sécurité'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['severity', 'investigated']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp}"

class SystemHealth(models.Model):
    component_name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('HEALTHY', 'Sain'),
            ('WARNING', 'Avertissement'),
            ('CRITICAL', 'Critique'),
            ('DOWN', 'Arrêté'),
        ]
    )
    response_time = models.FloatField(null=True, blank=True)
    cpu_usage = models.FloatField(null=True, blank=True)
    memory_usage = models.FloatField(null=True, blank=True)
    disk_usage = models.FloatField(null=True, blank=True)
    error_rate = models.FloatField(default=0.0)
    last_check = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Santé Système'
        verbose_name_plural = 'Santé Système'
    
    def __str__(self):
        return f"{self.component_name} - {self.status}"

class DataClassification(models.Model):
    """Classification des données pour le contrôle d'accès"""
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    classification_level = models.CharField(
        max_length=20,
        choices=[
            ('PUBLIC', 'Public'),
            ('RESTRICTED', 'Restreint'),
            ('CONFIDENTIAL', 'Confidentiel'),
            ('SECRET', 'Secret'),
            ('TOP_SECRET', 'Très Secret'),
        ]
    )
    authorized_users = models.ManyToManyField(User, blank=True)
    authorized_groups = models.JSONField(default=list, blank=True)
    classification_reason = models.TextField(blank=True)
    classified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='classified_data')
    classification_date = models.DateTimeField(auto_now_add=True)
    review_date = models.DateTimeField()
    
    class Meta:
        verbose_name = 'Classification de Données'
        verbose_name_plural = 'Classifications de Données'
        unique_together = ('content_type', 'object_id')
    
    def __str__(self):
        return f"Classification {self.classification_level} - {self.content_type}"