# views.py
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from academic_calendar.forms import AcademicCalendarForm
from utils.mixins import BaseAuthorizedModelView
from .models import AcademicCalendar

class AcademicCalendarIndexView(ListView):
    model = AcademicCalendar
    template_name = "pages/list.html"
    
class AcademicCalendarEventView(ListView):
    model = AcademicCalendar

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        data = [{
            "title": event.event_name,
            "start": event.event_date.isoformat(),
            "end": event.event_end_date.isoformat() if event.event_end_date else event.event_date.isoformat(),
        } for event in self.get_queryset()]
        return JsonResponse(data, safe=False)

class AcademicCalendarDetailView(BaseAuthorizedModelView, DetailView):
    model = AcademicCalendar


class AcademicCalendarCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = AcademicCalendar
    form_class = AcademicCalendarForm
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.add_academiccalendar'
    template_name = 'components/form.html'
    form_name = "Calendar"

class AcademicCalendarQuickCreateView(BaseAuthorizedModelView, CreateView):
    model = AcademicCalendar
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.add_academiccalendar'

class AcademicCalendarUpdateView(BaseAuthorizedModelView, UpdateView):
    model = AcademicCalendar
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.change_academiccalendar'
    
class AcademicCalendarDeleteView(BaseAuthorizedModelView, DeleteView):
    model = AcademicCalendar
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.delete_academiccalendar'