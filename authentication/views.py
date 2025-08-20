from django.contrib.auth import views as auth_views, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import HttpResponse
import logging

from .models import User, AccessAttempt
from security.models import SecurityEvent

logger = logging.getLogger('security')

class SecureLoginView(auth_views.LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        user = form.get_user()
        
        # Vérifier si le compte est verrouillé
        if user.is_account_locked():
            messages.error(self.request, 'Compte temporairement verrouillé. Réessayez plus tard.')
            return self.form_invalid(form)
        
        # Enregistrer la tentative de connexion réussie
        self.log_access_attempt(user.username, 'LOGIN', True, user)
        
        # Réinitialiser les tentatives échouées
        user.reset_failed_login()
        user.last_activity = timezone.now()
        user.save()
        
        # Enregistrer l'événement de sécurité
        SecurityEvent.objects.create(
            event_type='LOGIN',
            severity='LOW',
            user=user,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            description=f'Connexion réussie pour {user.username}'
        )
        
        messages.success(self.request, f'Bienvenue, {user.get_full_name()}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        username = form.data.get('username', '')
        
        # Enregistrer la tentative de connexion échouée
        self.log_access_attempt(username, 'FAILED_LOGIN', False)
        
        # Incrémenter les tentatives échouées si l'utilisateur existe
        try:
            user = User.objects.get(username=username)
            user.increment_failed_login()
            
            SecurityEvent.objects.create(
                event_type='FAILED_LOGIN',
                severity='MEDIUM',
                user=user,
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                description=f'Échec de connexion pour {username}'
            )
        except User.DoesNotExist:
            SecurityEvent.objects.create(
                event_type='FAILED_LOGIN',
                severity='HIGH',
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                description=f'Tentative de connexion avec un nom d\'utilisateur inexistant: {username}'
            )
        
        messages.error(self.request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        return super().form_invalid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def log_access_attempt(self, username, attempt_type, success, user=None):
        AccessAttempt.objects.create(
            user=user,
            username_attempted=username,
            attempt_type=attempt_type,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            success=success,
            details={
                'timestamp': timezone.now().isoformat(),
                'path': self.request.path,
            }
        )

class SecureLogoutView(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Enregistrer l'événement de déconnexion
            SecurityEvent.objects.create(
                event_type='LOGOUT',
                severity='LOW',
                user=request.user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                description=f'Déconnexion de {request.user.username}'
            )
            
            messages.success(request, 'Déconnexion réussie. À bientôt!')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SecurePasswordChangeView(LoginRequiredMixin, auth_views.PasswordChangeView):
    template_name = 'authentication/password_change.html'
    success_url = reverse_lazy('authentication:profile')
    
    def form_valid(self, form):
        # Enregistrer l'événement de changement de mot de passe
        SecurityEvent.objects.create(
            event_type='PASSWORD_CHANGE',
            severity='MEDIUM',
            user=self.request.user,
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            description=f'Changement de mot de passe pour {self.request.user.username}'
        )
        
        # Mettre à jour la date de changement de mot de passe
        self.request.user.password_last_changed = timezone.now()
        self.request.user.save()
        
        messages.success(self.request, 'Mot de passe modifié avec succès!')
        return super().form_valid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'authentication/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_sessions'] = self.request.user.sessions.filter(is_active=True)
        context['recent_access_attempts'] = AccessAttempt.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')[:10]
        return context

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'authentication/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        # Seuls les superviseurs et plus peuvent voir la liste des utilisateurs
        if self.request.user.rank not in ['SUPERVISOR', 'MANAGER', 'DIRECTOR', 'ADMINISTRATOR']:
            return User.objects.none()
        return User.objects.all().order_by('last_name', 'first_name')

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'authentication/user_detail.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        user = super().get_object()
        # Seuls les superviseurs et plus peuvent voir les détails des autres utilisateurs
        if (user != self.request.user and 
            self.request.user.rank not in ['SUPERVISOR', 'MANAGER', 'DIRECTOR', 'ADMINISTRATOR']):
            raise PermissionError("Accès refusé")
        return user

class SecurityEventsView(LoginRequiredMixin, ListView):
    template_name = 'authentication/security_events.html'
    context_object_name = 'events'
    paginate_by = 50
    
    def get_queryset(self):
        # Seuls les administrateurs peuvent voir tous les événements de sécurité
        if self.request.user.rank != 'ADMINISTRATOR':
            return SecurityEvent.objects.filter(user=self.request.user)
        return SecurityEvent.objects.all().order_by('-timestamp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_view_all'] = self.request.user.rank == 'ADMINISTRATOR'
        return context