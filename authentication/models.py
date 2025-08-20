from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from cryptography.fernet import Fernet
import base64
import os

class User(AbstractUser):
    SECURITY_LEVELS = [
        ('BASIC', 'Basique'),
        ('RESTRICTED', 'Restreint'),
        ('CONFIDENTIAL', 'Confidentiel'),
        ('SECRET', 'Secret'),
        ('TOP_SECRET', 'Très Secret'),
    ]
    
    RANKS = [
        ('AGENT', 'Agent'),
        ('SENIOR_AGENT', 'Agent Senior'),
        ('SUPERVISOR', 'Superviseur'),
        ('MANAGER', 'Manager'),
        ('DIRECTOR', 'Directeur'),
        ('ADMINISTRATOR', 'Administrateur'),
    ]
    
    employee_id = models.CharField(
        max_length=20, 
        unique=True,
        validators=[RegexValidator(r'^[A-Z]{2}\d{6}$', 'Format: XX123456')]
    )
    security_clearance = models.CharField(
        max_length=20, 
        choices=SECURITY_LEVELS, 
        default='BASIC'
    )
    rank = models.CharField(max_length=20, choices=RANKS, default='AGENT')
    department = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Format téléphone invalide')]
    )
    is_field_agent = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    password_last_changed = models.DateTimeField(default=timezone.now)
    two_factor_secret = models.CharField(max_length=255, blank=True, null=True)
    backup_codes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
    
    def is_account_locked(self):
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def increment_failed_login(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 3:
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=15)
        self.save()
    
    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    biography = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default='fr')
    timezone = models.CharField(max_length=50, default='Europe/Paris')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Profil Utilisateur'
        verbose_name_plural = 'Profils Utilisateurs'
    
    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Session Utilisateur'
        verbose_name_plural = 'Sessions Utilisateurs'
    
    def __str__(self):
        return f"Session de {self.user.username} - {self.ip_address}"

class AccessAttempt(models.Model):
    ATTEMPT_TYPES = [
        ('LOGIN', 'Connexion'),
        ('FAILED_LOGIN', 'Échec de connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('PASSWORD_CHANGE', 'Changement de mot de passe'),
        ('ACCOUNT_LOCKED', 'Compte verrouillé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username_attempted = models.CharField(max_length=150)
    attempt_type = models.CharField(max_length=20, choices=ATTEMPT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    details = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'Tentative d\'Accès'
        verbose_name_plural = 'Tentatives d\'Accès'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.attempt_type} - {self.username_attempted} - {self.timestamp}"