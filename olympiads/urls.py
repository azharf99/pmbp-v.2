from django.urls import path
from .views import OlympiadFieldIndexView, OlympiadFieldCreateView, OlympiadFieldDetailView, OlympiadFieldUpdateView, OlympiadFieldDeleteView,\
                    OlympiadReportIndexView, OlympiadReportCreateView, OlympiadReportUpdateView, OlympiadReportDetailView, OlympiadReportDeleteView,\
                    OlympiadReportOptionsView, OlympiadReportPrintView


urlpatterns = [
    path('', OlympiadFieldIndexView.as_view(), name='olympiad-field-list'),
    path('create/', OlympiadFieldCreateView.as_view(), name='olympiad-field-create'),
    path('detail/<slug:slug>/', OlympiadFieldDetailView.as_view(), name='olympiad-field-detail'),
    path('update/<slug:slug>/', OlympiadFieldUpdateView.as_view(), name='olympiad-field-update'),
    path('delete/<slug:slug>/', OlympiadFieldDeleteView.as_view(), name='olympiad-field-delete'),
    
    path('report/', OlympiadReportIndexView.as_view(), name='olympiad-report-list'),
    path('report/create/', OlympiadReportCreateView.as_view(), name='olympiad-report-create'),
    path('report/detail/<int:pk>/', OlympiadReportDetailView.as_view(), name='olympiad-report-detail'),
    path('report/update/<int:pk>/', OlympiadReportUpdateView.as_view(), name='olympiad-report-update'),
    path('report/delete/<int:pk>/', OlympiadReportDeleteView.as_view(), name='olympiad-report-delete'),

    path('report/options/<slug:slug>/', OlympiadReportOptionsView.as_view(), name='olympiad-report-options'),
    path('report/print/<slug:slug>/', OlympiadReportPrintView.as_view(), name='olympiad-report-print'),
]