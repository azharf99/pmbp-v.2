from django.urls import path
from dashboard.views import DashBooard, DownloadExcelInactiveStudent

urlpatterns = [
    path('', DashBooard.as_view(), name='dashboard'),
    path('nonaktif/', DownloadExcelInactiveStudent.as_view(), name='nonaktif'),

]