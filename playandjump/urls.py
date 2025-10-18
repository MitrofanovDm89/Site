"""
URL configuration for playandjump project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect

def robots_txt(request):
    return HttpResponse("User-agent: *\nAllow: /\n\nSitemap: https://www.playandjump.de/sitemap.xml", content_type="text/plain")

def redirect_old_pages(request):
    return redirect('/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('katalog/', include('catalog.urls')),
    path('robots.txt', robots_txt),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml')),
    # Редиректы для старых страниц
    path('huepfburg-zirkus/', redirect_old_pages),
    path('huepfburg-party/', redirect_old_pages),
    path('shooting-combo/', redirect_old_pages),
    path('stockfangen/', redirect_old_pages),
    path('huepfburg-polizei/', redirect_old_pages),
    path('fussball-darts/', redirect_old_pages),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 