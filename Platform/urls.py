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
from django.views.generic import ListView
from dashboard.views import HomeView, HumasDashboardView
from galleries.models import Gallery
from utils.views import LatestPostsAtomFeed, LatestPostsFeed, ProkerPMBPView, SMAITHomeWiew
from utils_piket.menu_link import export_home_kwargs
from utils_piket.views import DashboardListView, ReporterRecapDownloadExcelView, ReporterRecapListView, TeacherAbsenceDetailDownloadExcelView, TeacherAbsenceDownloadExcelView, TeacherAbsenceListView, TeacherPutriRecapListView, TeacherRecapDetailView, TeacherRecapDownloadExcelView, TeacherRecapListView, device_webhook, message_webhook, tracking_webhook
from .sitemaps import StaticViewSitemap
from raker.views import ProgramKerjaCreateView, ProgramKerjaDeleteView, ProgramKerjaUpdateView, proker

sitemaps = {
    "static": StaticViewSitemap,
}

class IndexView(ListView):
    model = Gallery

urlpatterns = [
    path('', SMAITHomeWiew.as_view(), name='app-index'),
    path('accounts/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('class/', include('classes.urls')),
    path('blog/', include('blog.urls')),
    path('calendar/', include('academic_calendar.urls')),
    path('course/', include('courses.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('device/', device_webhook, name='device-status'),
    path('galleries/', include("galleries.urls")),
    path('files/', include('files.urls')),

    path('humas/', IndexView.as_view(template_name="humas.html"), name='humas-index'),
    path('humas/alumni/', include("alumni.urls")),
    path('humas/dashboard/', HumasDashboardView.as_view(), name="dashboard"),
    path('humas/private/', include("private.urls")),
    path('humas/students/', include("students.urls")),


    path('piket/', TemplateView.as_view(template_name='piket.html'), export_home_kwargs("home", "PIKET"), "piket-index"),
    path('piket/menu/', TemplateView.as_view(template_name='menu.html'), export_home_kwargs("menu", "MENU PIKET"), "menu"),
    path('piket/dashboard/', DashboardListView.as_view(), export_home_kwargs("dashboard", "DASHBOARD PIKET"), "piket-dashboard"),
    path('piket/dashboard/teachers/', TeacherRecapListView.as_view(), export_home_kwargs("dashboard", "DATA KEHADIRAN GURU"), "dashboard-teachers"),
    path('piket/dashboard/teachers/putri/', TeacherPutriRecapListView.as_view(), export_home_kwargs("dashboard", "DATA KEHADIRAN GURU  PUTRI"), "putri-dashboard-teachers"),
    path('piket/dashboard/teachers/download/', TeacherRecapDownloadExcelView.as_view(), export_home_kwargs("dashboard", "DOWNLOAD TEACHER REPORT"), "dashboard-teachers-download"),
    path('piket/dashboard/teachers/absence/', TeacherAbsenceListView.as_view(), export_home_kwargs("dashboard", "DATA KETIDAKHADIRAN GURU"), "dashboard-teachers-absence"),
    path('piket/dashboard/teachers/absence/download/', TeacherAbsenceDownloadExcelView.as_view(), export_home_kwargs("dashboard", "DOWNLOAD DATA KETIDAKHADIRAN GURU"), "dashboard-teachers-absence-download"),
    path('piket/dashboard/teachers/<int:teacher_id>/detail/', TeacherRecapDetailView.as_view(), export_home_kwargs("dashboard", "DATA DETAIL KETIDAKHADIRAN GURU"), "dashboard-teachers-detail"),
    path('piket/dashboard/teachers/<int:teacher_id>/detail/download/', TeacherAbsenceDetailDownloadExcelView.as_view(), export_home_kwargs("dashboard", "DATA DETAIL KETIDAKHADIRAN GURU"), "dashboard-teachers-detail-download"),
    path('piket/dashboard/reporters/', ReporterRecapListView.as_view(), export_home_kwargs("dashboard", "DATA KEHADIRAN PETUGAS PIKET"), "dashboard-reporters"),
    path('piket/dashboard/reporters/download/', ReporterRecapDownloadExcelView.as_view(), export_home_kwargs("dashboard", "DOWNLOAD KEHADIRAN PETUGAS PIKET"), "dashboard-reporters-download"),
    path('piket/report/', include('reports.urls')),
    path('piket/schedule/', include('schedules.urls')),


    path('pmbp/', HomeView.as_view(), name='pmbp-index'),
    path('pmbp/extracurriculars/', include('extracurriculars.urls')),
    path('pmbp/lpj/', include('raker.urls')),
    path('pmbp/report/', include('laporan.urls')),
    path('pmbp/nilai/', include('nilai.urls')),
    path('pmbp/prestasi/', include('prestasi.urls')),
    path('pmbp/proker/', ProkerPMBPView.as_view(), name='proker'),
    path("pmbp/proker/create/", ProgramKerjaCreateView.as_view(), name="proker-create"),
    path("pmbp/proker/update/<int:pk>/", ProgramKerjaUpdateView.as_view(), name="proker-update"),
    path("pmbp/proker/delete/<int:pk>/", ProgramKerjaDeleteView.as_view(), name="proker-delete"),
    path('pmbp/olympiads/', include('olympiads.urls')),
    path('pmbp/projects/', include('projects.urls')),

    path("rss/", LatestPostsFeed(), name="post-feed"),
    path("atom/", LatestPostsAtomFeed(), name="post-atom-feed"),

    path('dashboard/', include('dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('message/', message_webhook, name='message-status'),
    path('tracking/', tracking_webhook, name='tracking-status'),
    path("pages/", include("django.contrib.flatpages.urls")),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('students/', include('students.urls')),
    path('tahfidz/', include("tahfidz.urls")),
    # path('timetable/', include("scheduler.urls")),
    path('userlog/', include('userlog.urls')),
    path(
    "sitemap.xml",
    sitemap,
    {"sitemaps": sitemaps},
    name="django.contrib.sitemaps.views.sitemap",
    ),
    path('service-worker.js', TemplateView.as_view(template_name="service-worker.js", content_type='application/javascript')),
]


if settings.DEBUG:
    urlpatterns = [
        *urlpatterns,
        # path('attendance/', include('attendance.urls')),
        path("__debug__/", include("debug_toolbar.urls")),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    path("about-us/", flatpage, {"url": "/about-us/"}, name="about"),
    path("license/", flatpage, {"url": "/license/"}, name="license"),
]
