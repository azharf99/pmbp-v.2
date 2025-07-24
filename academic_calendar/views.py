# views.py
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import AcademicCalendar

class AcademicCalendarIndexView(ListView):
    model = AcademicCalendar
    

class AcademicCalendarDetailView(DetailView):
    model = AcademicCalendar


class AcademicCalendarCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = AcademicCalendar
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.add_academiccalendar'

class AcademicCalendarQuickCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = AcademicCalendar
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.add_academiccalendar'

class AcademicCalendarUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = AcademicCalendar
    fields = '__all__'
    template_name = 'nilai/score_form.html'
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.change_academiccalendar'
    
class AcademicCalendarDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = AcademicCalendar
    success_url = reverse_lazy('calendar-list')
    permission_required = 'academic_calendar.delete_academiccalendar'