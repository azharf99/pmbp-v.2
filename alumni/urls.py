from django.urls import path
from alumni.views import AlumniDashboardView, AlumniSearchView, AlumniIndexView, AlumniCreateView, \
                        AlumniDetailView, AlumniUpdateView, AlumniDeleteView, AlumniQuickUploadView,\
                        AlumniDownloadExcelView

app_name = "alumni"

urlpatterns = [
    path("", AlumniIndexView.as_view(), {"site_title": "ALUMNI LIST - SMA IT AL BINAA"}, name="alumni-list"),
    path("dashboard/", AlumniDashboardView.as_view(), {"site_title": "ALUMNI DASHBOARD - SMA IT AL BINAA"}, name="alumni-dashboard"),
    path("search/", AlumniSearchView.as_view(), {"site_title": "ALUMNI SEARCH - SMA IT AL BINAA"}, name="alumni-search"),
    path("create/", AlumniCreateView.as_view(), {"site_title": "CREATE ALUMNI - SMA IT AL BINAA"}, name="alumni-create"),
    path("download/", AlumniDownloadExcelView.as_view(), {"site_title": "DOWNLOAD ALUMNI - SMA IT AL BINAA"}, name="alumni-download"),
    path("quick-upload/", AlumniQuickUploadView.as_view(), {"site_title": "QUICK UPLOAD ALUMNI - SMA IT AL BINAA"}, name="alumni-quick-upload"),
    path("detail/<int:pk>/", AlumniDetailView.as_view(), {"site_title": "ALUMNI DETAIL - SMA IT AL BINAA"}, name="alumni-detail"),
    path("update/<int:pk>/", AlumniUpdateView.as_view(), {"site_title": "UPDATE ALUMNI - SMA IT AL BINAA"}, name="alumni-update"),
    path("delete/<int:pk>/", AlumniDeleteView.as_view(), {"site_title": "DELETE ALUMNI - SMA IT AL BINAA"}, name="alumni-delete"),
]