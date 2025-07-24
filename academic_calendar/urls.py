from django.urls import path

from academic_calendar.views import AcademicCalendarCreateView, AcademicCalendarDeleteView, \
                                    AcademicCalendarDetailView, AcademicCalendarIndexView, \
                                    AcademicCalendarQuickCreateView, AcademicCalendarUpdateView

urlpatterns = [
    path('', AcademicCalendarIndexView.as_view(), name='calendar-list'),
    path('create/', AcademicCalendarCreateView.as_view(), name='calendar-create'),
    path('quick-create/', AcademicCalendarQuickCreateView.as_view(), name='calendar-quick-create'),
    path('detail/<int:pk>/', AcademicCalendarDetailView.as_view(), name='calendar-detail'),
    path('update/<int:pk>/', AcademicCalendarUpdateView.as_view(), name='calendar-update'),
    path('delete/<int:pk>/', AcademicCalendarDeleteView.as_view(), name='calendar-delete'),
]