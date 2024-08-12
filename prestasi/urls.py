from django.urls import path
from prestasi.views import PrestasiIndexView, PrestasiCreateView, PrestasiDetailView, PrestasiUpdateView, PrestasiDeleteView, \
                            ProgramPrestasiIndexView, ProgramPrestasiCreateView, ProgramPrestasiUpdateView, ProgramPrestasiDeleteView,\
                            PretasiPrintExcelView, PrestasiPrintExcelThisYearView, ProgramPrestasiPrintExcelThisYearView


urlpatterns = [
    path('', PrestasiIndexView.as_view(), name='prestasi-list'),
    path('create/', PrestasiCreateView.as_view(), name='prestasi-create'),
    path('detail/<int:pk>/', PrestasiDetailView.as_view(), name='prestasi-detail'),
    path('update/<int:pk>/', PrestasiUpdateView.as_view(), name='prestasi-update'),
    path('delete/<int:pk>/', PrestasiDeleteView.as_view(), name='prestasi-delete'),

    path('program/', ProgramPrestasiIndexView.as_view(), name='program-prestasi-list'),
    path('program/create/', ProgramPrestasiCreateView.as_view(), name='program-prestasi-create'),
    path('program/detail/<int:pk>/', ProgramPrestasiUpdateView.as_view(), name='program-prestasi-detail'),
    path('program/update/<int:pk>/', ProgramPrestasiUpdateView.as_view(), name='program-prestasi-update'),
    path('program/delete/<int:pk>/', ProgramPrestasiDeleteView.as_view(), name='program-prestasi-delete'),

    path('downloads/', PretasiPrintExcelView.as_view(), name='prestasi-download'),
    path('download/', PrestasiPrintExcelThisYearView.as_view(), name='prestasi-download-tahun-ini'),
    path('program/download/', ProgramPrestasiPrintExcelThisYearView.as_view(), name='program-prestasi-download'),
]