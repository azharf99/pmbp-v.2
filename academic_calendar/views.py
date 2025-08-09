# views.py
import calendar
from datetime import date, timedelta
from django.utils import timezone
from django.utils.safestring import mark_safe
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from academic_calendar.forms import AcademicCalendarForm
from utils.mixins import BaseAuthorizedModelView
from .models import AcademicCalendar


class CalendarHTML(calendar.HTMLCalendar):
    def __init__(self, events):
        super().__init__()
        self.events = events

    def formatday(self, day, weekday):
        if day == 0:
            return '<td></td>'  # padding day

        # Events that occur on this day (within start and end range)
        events_today = [
            event for event in self.events
            if event.event_date <= date(self.year, self.month, day) and
               (event.event_end_date is None or event.event_end_date >= date(self.year, self.month, day))
        ]

        events_html = ''.join(f'<li>{event.event_name}</li>' for event in events_today)
        return f"<td class='{self.cssclasses[weekday]}'><span>{day}</span><ul>{events_html}</ul></td>"

    def formatweek(self, theweek):
        return f"<tr>{''.join(self.formatday(d, wd) for (d, wd) in theweek)}</tr>"

    def formatmonth(self, year, month, withyear=True):
        self.year = year
        self.month = month
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="month">\n'
        cal += f'{self.formatmonthname(year, month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(year, month):
            cal += f'{self.formatweek(week)}\n'
        cal += '</table>'
        return cal


def get_month(year, month, delta):
    new_date = date(year, month, 1) + timedelta(days=delta * 31)
    return new_date.year, new_date.month

class AcademicCalendarIndexView(ListView):
    model = AcademicCalendar
    template_name = "pages/list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        # Get year/month from query params, or use today
        today = date.today()
        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))

        # Calculate prev/next months
        prev_year, prev_month = get_month(year, month, -1)
        next_year, next_month = get_month(year, month, 1)

        # Get all events that overlap this month
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        events = AcademicCalendar.objects.filter(
            event_date__lte=last_day,
        ).filter(
            event_end_date__gte=first_day
        ) | AcademicCalendar.objects.filter(
            event_date__gte=first_day,
            event_date__lte=last_day,
            event_end_date__isnull=True
        )

        # Render calendar
        cal = CalendarHTML(events).formatmonth(year, month)
        c.update({
            'calendar': mark_safe(cal),
            'year': year,
            'month': month,
            'prev_year': prev_year,
            'prev_month': prev_month,
            'next_year': next_year,
            'next_month': next_month,
        })
        return c
    
class AcademicCalendarEventView(ListView):
    model = AcademicCalendar

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        data = [{
            "title": event.event_name,
            "start": event.event_date.isoformat(),
            "end": event.event_end_date.isoformat() if event.event_end_date else event.date.isoformat(),
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