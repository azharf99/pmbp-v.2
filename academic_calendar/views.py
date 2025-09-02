# views.py
from typing import Any
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from academic_calendar.forms import AcademicCalendarForm
from utils.mixins import BaseLoginAndPermissionFormView, BaseLoginAndPermissionModelDeleteView, BaseLoginAndPermissionRequiredView, TitleView
from .models import AcademicCalendar

class AcademicCalendarIndexView(TitleView, ListView):
    model = AcademicCalendar
    template_name = "pages/calendar.html"
    title_of_table = "Kalender Akademik"
    
class AcademicCalendarEventView(TitleView, ListView):
    model = AcademicCalendar

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        data = [{
            "id": event.id,
            "title": event.event_name,
            "start": event.event_date.isoformat(),
            "end": event.event_end_date.isoformat() if event.event_end_date else event.event_date.isoformat(),
            "description": event.event_notes,
        } for event in self.get_queryset()]
        return JsonResponse(data, safe=False)

class AcademicCalendarDetailView(BaseLoginAndPermissionRequiredView, DetailView):
    model = AcademicCalendar
    permission_required = 'academic_calendar.view_academiccalendar'


class AcademicCalendarCreateView(BaseLoginAndPermissionFormView, CreateView):
    model = AcademicCalendar
    form_class = AcademicCalendarForm
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.add_academiccalendar'
    template_name = 'pages/form.html'
    links = ['calendar-list', 'calendar-detail', 'calendar-update', 'calendar-delete', 'calendar-event-list']

class AcademicCalendarQuickCreateView(BaseLoginAndPermissionFormView, CreateView):
    model = AcademicCalendar
    fields = '__all__'
    template_name = 'pages/form.html'
    links = ['calendar-list', 'calendar-detail', 'calendar-update', 'calendar-delete', 'calendar-event-list']
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.add_academiccalendar'

class AcademicCalendarUpdateView(BaseLoginAndPermissionFormView, UpdateView):
    model = AcademicCalendar
    form_class = AcademicCalendarForm
    template_name = 'pages/form.html'
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.change_academiccalendar'
    links = ['calendar-list', 'calendar-detail', 'calendar-update', 'calendar-delete', 'calendar-event-list']

    
class AcademicCalendarDeleteView(BaseLoginAndPermissionModelDeleteView):
    model = AcademicCalendar
    success_url = reverse_lazy('calendar-list')
    template_name = 'pages/delete.html'
    permission_required = 'academic_calendar.delete_academiccalendar'
    links = ['calendar-list', 'calendar-detail', 'calendar-update', 'calendar-delete', 'calendar-event-list']