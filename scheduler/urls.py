from django.urls import path
from . import views

urlpatterns = [
    # URL for displaying the timetable
    path('', views.timetable_view, name='timetable_view'),
    # URL for triggering the generation process
    path('generate/', views.generate_timetable_view, name='generate_timetable'),
]