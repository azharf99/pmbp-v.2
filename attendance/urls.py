from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='attendance-list'),
    path('dashboard-data/', views.dashboard_data, name='dashboard_data'),
    path('register/', views.register_student, name='register_student'),
    path('attendance/', views.take_attendance, name='take_attendance'),
    path('realtime/', views.realtime_attendance, name='realtime_attendance'),
    path('records/', views.attendance_records, name='attendance_records'),
]