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
from django.contrib.sitemaps.views import sitemap
from django.contrib.flatpages.views import flatpage
from dashboard.views import HomeView
from utils.views import CurrationListView, LPJPMBPView, ProkerPMBPView
from .sitemaps import StaticViewSitemap
from raker.views import ProgramKerjaCreateView, ProgramKerjaDeleteView, ProgramKerjaUpdateView, proker

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path('', HomeView.as_view(), name='app-index'),
    path('accounts/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('extracurriculars/', include('extracurriculars.urls')),
    path('files/', include('files.urls')),
    path('report/', include('laporan.urls')),
    path('kurasi/', CurrationListView.as_view(), {}, "curration-list"),
    path('logs/', include('userlog.urls')),
    path('lpj/', include('raker.urls')),
    path('nilai/', include('nilai.urls')),
    path('prestasi/', include('prestasi.urls')),
    path('proker/', ProkerPMBPView.as_view(), name='proker'),
    path("proker/create/", ProgramKerjaCreateView.as_view(), name="proker-create"),
    path("proker/update/<int:pk>/", ProgramKerjaUpdateView.as_view(), name="proker-update"),
    path("proker/delete/<int:pk>/", ProgramKerjaDeleteView.as_view(), name="proker-delete"),
    path('olympiads/', include('olympiads.urls')),
    path("pages/", include("django.contrib.flatpages.urls")),
    path('projects/', include('projects.urls')),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('students/', include('students.urls')),
    path(
    "sitemap.xml",
    sitemap,
    {"sitemaps": sitemaps},
    name="django.contrib.sitemaps.views.sitemap",
    ),
    path('service-worker.js', TemplateView.as_view(template_name="service-worker.js", content_type='application/javascript')),
    path("__debug__/", include("debug_toolbar.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    path("about-us/", flatpage, {"url": "/about-us/"}, name="about"),
    path("license/", flatpage, {"url": "/license/"}, name="license"),
]
