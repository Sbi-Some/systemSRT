from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('api/intelligence/', include('intelligence.urls')),
    path('api/analysis/', include('analysis.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('intelligence/', include('intelligence.urls')),
    path('analysis/', include('analysis.urls')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuration de l'admin
admin.site.site_header = "SRT - Administration"
admin.site.site_title = "SRT Admin"
admin.site.index_title = "Système de Renseignement Tactique"