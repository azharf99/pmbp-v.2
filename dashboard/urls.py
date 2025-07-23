from django.urls import path
from dashboard.views import DashboardView, InactiveReportView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('inactive/', InactiveReportView.as_view(), name='dashboard-inactive'),
]