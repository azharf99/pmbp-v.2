from django.urls import path
from .views import CreateBidangKsmView, DetailBidangKSMView, UpdateBidangKsmView, DeleteBidangKsmView, KsmIndexView, \
                    CreateSiswaKsmView, UpdateSiswaKsmView, DeleteSiswaKsmView, CreateLaporanKsmView, UpdateLaporanKsmView, DeleteLaporanKsmView,\
                    PrintKSMReport

app_name = 'ksm'
urlpatterns = [
    path('', KsmIndexView.as_view(), name='ksm-index'),
    path('input', CreateBidangKsmView.as_view(), name='bidang-ksm-input'),
    path('edit/<int:pk>', UpdateBidangKsmView.as_view(), name='bidang-ksm-edit'),
    path('delete/<int:pk>', DeleteBidangKsmView.as_view(), name='bidang-ksm-delete'),
    path('<slug:slug>', DetailBidangKSMView.as_view(), name='detail-bidang-ksm'),
    path('<slug:slug>/input/siswa', CreateSiswaKsmView.as_view(), name='siswa-ksm-input'),
    path('<slug:slug>/delete/siswa/<int:pk>', DeleteSiswaKsmView.as_view(), name='siswa-ksm-delete'),
    path('<slug:slug>/input/laporan', CreateLaporanKsmView.as_view(), name='laporan-ksm-input'),
    path('<slug:slug>/edit/laporan/<int:pk>', UpdateLaporanKsmView.as_view(), name='laporan-ksm-edit'),
    path('<slug:slug>/delete/laporan/<int:pk>', DeleteLaporanKsmView.as_view(), name='laporan-ksm-delete'),
    path('<slug:slug>/print', PrintKSMReport.as_view(), name='laporan-ksm-print'),
    # path('<slug:slug>/print2', views.cetak_laporan_ksmp, name='laporan-ksmp-print'),
]