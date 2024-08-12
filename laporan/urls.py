from django.urls import path
from laporan.views import ReportIndexView, ReportDetailView, PrintToPrintView, \
                         ReportOptionsView, ReportCreateView, ReportUpdateView, ReportDeleteView

urlpatterns = [
    path('', ReportIndexView.as_view(), name='report-list'),
    path('create/', ReportCreateView.as_view(), name='report-create'),
    path('detail/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('update/<int:pk>/', ReportUpdateView.as_view(), name='report-update'),
    path('delete/<int:pk>/', ReportDeleteView.as_view(), name='report-delete'),

    path('print/<slug:slug>/', PrintToPrintView.as_view(), name='report-print'),
    path('options/<slug:slug>/', ReportOptionsView.as_view(), name='report-options'),

    # path('print2/<slug:slug>/', ReportEkskulPrintView.as_view(), name='report-print-v2'),
    # path('<int:pk>/input/', ReportInputView.as_view(), name='report-input'),
    # path('<int:pk>/detail/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    # path('<int:pk>/edit/<int:pk>/', ReportUpdateView.as_view(), name='report-edit'),
    # path('<int:pk>/delete/<int:pk>/', ReportDeleteView.as_view(), name='report-delete'),
]