from django.urls import path
from dashboard.views import Dashboard, InactiveReportView

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('inactive/', InactiveReportView.as_view(), name='dashboard-inactive'),
]