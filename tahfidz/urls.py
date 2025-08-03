from django.urls import path
from tahfidz.views import QuickFillUnsubmittedTilawahView, TahfidzIndexView, TahfidzCreateView, TahfidzDetailView, TahfidzUpdateView, TahfidzDeleteView, \
                            TahfidzQuickUploadView, TahfidzQuickCSVUploadView, TilawahClassReportView, TilawahCreateView, TilawahDeleteView, \
                            TilawahDetailView, TilawahIndexView, TilawahQuickUploadView, TilawahUpdateView
app_name = "tahfidz"

urlpatterns = [
    path("", TahfidzIndexView.as_view(), name="tahfidz-list"),
    path("create/", TahfidzCreateView.as_view(), name="tahfidz-create"),
    path("quick-create/", TahfidzQuickUploadView.as_view(), name="tahfidz-quick-create"),
    path("quick-create-csv/", TahfidzQuickCSVUploadView.as_view(), name="tahfidz-quick-create-csv"),
    path("detail/<int:pk>/", TahfidzDetailView.as_view(), name="tahfidz-detail"),
    path("update/<int:pk>/", TahfidzUpdateView.as_view(), name="tahfidz-update"),
    path("delete/<int:pk>/", TahfidzDeleteView.as_view(), name="tahfidz-delete"),
    path("tilawah/", TilawahIndexView.as_view(), name="tilawah-list"),
    path("tilawah/quick-fill/", QuickFillUnsubmittedTilawahView.as_view(), name="tilawah-quick-fill"),
    path("tilawah/create/", TilawahCreateView.as_view(), name="tilawah-create"),
    path("tilawah/class_report/", TilawahClassReportView.as_view(), name="tilawah-class-report"),
    path("tilawah/quick-create/", TilawahQuickUploadView.as_view(), name="tilawah-quick-create"),
    path("tilawah/detail/<int:pk>/", TilawahDetailView.as_view(), name="tilawah-detail"),
    path("tilawah/update/<int:pk>/", TilawahUpdateView.as_view(), name="tilawah-update"),
    path("tilawah/delete/<int:pk>/", TilawahDeleteView.as_view(), name="tilawah-delete"),
]