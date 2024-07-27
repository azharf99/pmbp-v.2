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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.flatpages import views
from deskripsi.views import HomeView, menu_view
from ekskul.views import MyLoginView, logout_view, register, edit_password, edit_profil_view, profil_view, edit_username, webhook_view
from userlog.views import UserLogindex
from .sitemaps import StaticViewSitemap

def struktur(request):
    return render(request, 'struktur.html')

def unduh(request):
    return render(request, 'unduh.html')

def not_available(request):
    return render(request, 'notavailable.html')

def restricted(request):
    return render(request, 'restricted.html')

def proker(request):
    return render(request, 'proker.html')

def lpj(request):
    return render(request, 'lpj.html')

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path('', HomeView.as_view(), name='app-index'),
    path('alumni/', include('alumni.urls')),
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('menu', menu_view, name='menu'),
    path('log/', UserLogindex, name='log-index'),
    path('admin/', admin.site.urls),
    path('login/', MyLoginView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('password/', edit_password, name='password'),
    path('username-change/', edit_username, name='username-change'),
    path('accounts/login/', MyLoginView.as_view(), name='login'),
    path('accounts/profile/', profil_view, name='profil'),
    path('profil/edit', edit_profil_view, name='edit-profil'),
    path('logout/', logout_view, name='logout'),
    path('laporan/', include('laporan.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('nilai/', include('nilai.urls')),
    path('data/', include('ekskul.urls')),
    path('prestasi/', include('prestasi.urls')),
    path('osn/', include('osn.urls')),
    path('ksm/', include('ksm.urls')),
    path('struktur/', struktur, name='struktur-page'),
    path('unduh/', unduh, name='unduh-page'),
    path('notavailable/', not_available, name='not-available'),
    path('restricted/', restricted, name='restricted'),
    path('webhook/', webhook_view, name='webhook'),
    path('proker/', proker, name='proker'),
    path('lpj/', lpj, name='lpj'),
    path("__debug__/", include("debug_toolbar.urls")),
    path("pages/", include("django.contrib.flatpages.urls")),
    path(
    "sitemap.xml",
    sitemap,
    {"sitemaps": sitemaps},
    name="django.contrib.sitemaps.views.sitemap",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



urlpatterns += [
    path("about-us/", views.flatpage, {"url": "/about-us/"}, name="about"),
    path("license/", views.flatpage, {"url": "/license/"}, name="license"),
]
