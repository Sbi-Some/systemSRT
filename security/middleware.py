import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import SecurityEvent

logger = logging.getLogger('security')

class SecurityAuditMiddleware(MiddlewareMixin):
    """Middleware pour l'audit de sécurité"""
    
    def process_request(self, request):
        """Enregistre les tentatives d'accès"""
        # Ignorer les fichiers statiques et admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        # Enregistrer l'accès
        user = request.user if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser) else None
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Log des accès sensibles
        if any(sensitive_path in request.path for sensitive_path in ['/api/', '/intelligence/', '/analysis/']):
            logger.info(f"Accès sensible: {request.path} - User: {user} - IP: {ip_address}")
        
        return None
    
    def process_response(self, request, response):
        """Traite la réponse pour détecter les erreurs de sécurité"""
        if response.status_code == 403:
            self.log_security_event(
                request, 
                'PERMISSION_DENIED', 
                'HIGH',
                f"Accès refusé à {request.path}"
            )
        elif response.status_code == 401:
            self.log_security_event(
                request,
                'FAILED_LOGIN',
                'MEDIUM',
                f"Authentification échouée pour {request.path}"
            )
        
        return response
    
    def get_client_ip(self, request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_security_event(self, request, event_type, severity, description):
        """Enregistre un événement de sécurité"""
        try:
            user = request.user if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser) else None
            SecurityEvent.objects.create(
                event_type=event_type,
                severity=severity,
                user=user,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                description=description,
                additional_data={
                    'path': request.path,
                    'method': request.method,
                    'get_params': dict(request.GET),
                }
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'événement de sécurité: {e}")