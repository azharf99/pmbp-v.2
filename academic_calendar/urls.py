from django.urls import path

from academic_calendar.views import AcademicCalendarCreateView, AcademicCalendarDeleteView, \
                                    AcademicCalendarDetailView, AcademicCalendarEventView, AcademicCalendarIndexView, \
                                    AcademicCalendarQuickCreateView, AcademicCalendarUpdateView

urlpatterns = [
    path('', AcademicCalendarIndexView.as_view(), {"site_title": "ACADEMIC CALENDAR LIST - SMA IT AL BINAA"}, name='calendar-list'),
    path('events/', AcademicCalendarEventView.as_view(), {"site_title": "ACADEMIC CALENDAR EVENT LIST - SMA IT AL BINAA"}, name='calendar-event-list'),
    path('create/', AcademicCalendarCreateView.as_view(), {"site_title": "CREATE ACADEMIC CALENDAR - SMA IT AL BINAA"}, name='calendar-create'),
    path('quick-create/', AcademicCalendarQuickCreateView.as_view(), {"site_title": "QUICK CREATE ACADEMIC CALENDAR - SMA IT AL BINAA"}, name='calendar-quick-create'),
    path('detail/<int:pk>/', AcademicCalendarDetailView.as_view(), {"site_title": "ACADEMIC CALENDAR DETAIL - SMA IT AL BINAA"}, name='calendar-detail'),
    path('update/<int:pk>/', AcademicCalendarUpdateView.as_view(), {"site_title": "UPDATE ACADEMIC CALENDAR - SMA IT AL BINAA"}, name='calendar-update'),
    path('delete/<int:pk>/', AcademicCalendarDeleteView.as_view(), {"site_title": "DELETE ACADEMIC CALENDAR - SMA IT AL BINAA"}, name='calendar-delete'),
]