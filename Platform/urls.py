"""Platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.generic.base import TemplateView

import deskripsi.views
import ekskul.views
import userlog.views


def struktur(request):
    return render(request, 'struktur.html')

def unduh(request):
    return render(request, 'unduh.html')

def not_available(request):
    return render(request, 'notavailable.html')

def restricted(request):
    return render(request, 'restricted.html')



urlpatterns = [
    path('', deskripsi.views.HomeView.as_view(), name='app-index'),
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('menu', deskripsi.views.menu_view, name='menu'),
    path('log/', userlog.views.index, name='log-index'),
    path('admin/', admin.site.urls),
    path('login/', ekskul.views.login_view, name='login'),
    path('register/', ekskul.views.register, name='register'),
    path('password/', ekskul.views.edit_password, name='password'),
    path('username-change/', ekskul.views.edit_username, name='username-change'),
    path('profil/', ekskul.views.profil_view, name='profil'),
    path('profil/edit', ekskul.views.edit_profil_view, name='edit-profil'),
    path('logout/', ekskul.views.logout_view, name='logout'),
    # path('ekskul/', deskripsi.views.ekskul_view, name='ekskul-page'),
    path('laporan/', include('laporan.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('proposal/', include('proposal.urls')),
    path('nilai/', include('nilai.urls')),
    path('data/', include('ekskul.urls')),
    path('inventaris/', include('inventaris.urls')),
    # path('timeline/', include('timeline.urls')),
    path('prestasi/', include('prestasi.urls')),
    path('osn/', include('osn.urls')),
    path('struktur/', struktur, name='struktur-page'),
    path('unduh/', unduh, name='unduh-page'),
    path('notavailable/', not_available, name='not-available'),
    path('restricted/', restricted, name='restricted'),
    path('webhook/', ekskul.views.webhook_view, name='webhook'),
    path("__debug__/", include("debug_toolbar.urls")),
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
