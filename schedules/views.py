from datetime import datetime
from django.contrib import messages
from django.core.management import call_command
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from typing import Any
from django.urls import reverse_lazy
from classes.models import Class
from schedules.forms import ScheduleForm
from schedules.models import Period, Schedule
from utils_piket.mixins import BaseAuthorizedFormView, BaseModelDateBasedListView, BaseModelDeleteView, BaseModelUploadView, BaseAuthorizedModelView, ModelDownloadExcelView
from utils_piket.constants import WEEKDAYS

# Create your views here.

class ScheduleView(BaseAuthorizedModelView, ListView):
    model = Schedule
    menu_name = 'schedule'
    template_name = 'schedules/schedule_view.html'
    queryset = Schedule.objects.select_related("schedule_course", "schedule_course__teacher", "schedule_course__course", "schedule_class", "schedule_time")
    permission_required = 'schedules.view_schedule'
    raise_exception = False

    def get_queryset(self) -> QuerySet[Any]:
        query_day = self.request.GET.get('query_day')
        if not query_day:
            query_day = WEEKDAYS.get(datetime.now().weekday())
        groupped_qs = []
        for i in range(1, 10):
            qs = self.queryset.filter(schedule_day=query_day, schedule_time=i, type="putra")\
                        .values('schedule_class__short_class_name', 
                                'schedule_course__teacher__teacher_name',
                                'schedule_course__course_code',
                                'schedule_course__course__short_name')\
                        .order_by('schedule_class__short_class_name')
            if qs.exists():
                groupped_qs.append(qs)
            else:
                groupped_qs.append([{"schedule_class__short_class_name": "Kosong", 
                                     "schedule_course__teacher__teacher_name": "Kosong",
                                     "schedule_course__course_code": "Kosong",
                                     "schedule_course__course__short_name": "Kosong"
                                     } for j in range(15)])
        return groupped_qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query_type"] = self.request.GET.get('query_type', 'code')
        if self.request.GET.get('query_day'):
            context["query_day"] = self.request.GET.get('query_day')
        else:
            context["query_day"] = WEEKDAYS.get(datetime.now().weekday())
        context["class"] = Class.objects.filter(category="Putra")
        return context
    

class SchedulePutriView(BaseAuthorizedModelView, ListView):
    model = Schedule
    menu_name = 'schedule'
    template_name = 'schedules/schedule_view.html'
    queryset = Schedule.objects.select_related("schedule_course", "schedule_course__teacher", "schedule_course__course", "schedule_class", "schedule_time")
    permission_required = 'schedules.view_schedule'
    raise_exception = False

    def get_queryset(self) -> QuerySet[Any]:
        query_day = self.request.GET.get('query_day')
        if not query_day:
            query_day = WEEKDAYS.get(datetime.now().weekday())
        groupped_qs = []
        for i in range(1, 10):
            qs = self.queryset.filter(schedule_day=query_day, schedule_time=i, type="putri")\
                        .values('schedule_class__short_class_name', 
                                'schedule_course__teacher__teacher_name',
                                'schedule_course__course_code',
                                'schedule_course__course__short_name')\
                        .order_by('schedule_class__short_class_name')
            if qs.exists():
                groupped_qs.append(qs)
            else:
                groupped_qs.append([{"schedule_class__short_class_name": "Kosong", 
                                     "schedule_course__teacher__teacher_name": "Kosong",
                                     "schedule_course__course_code": "Kosong",
                                     "schedule_course__course__short_name": "Kosong"
                                     } for j in range(15)])
        return groupped_qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query_type"] = self.request.GET.get('query_type', 'code')
        if self.request.GET.get('query_day'):
            context["query_day"] = self.request.GET.get('query_day')
        else:
            context["query_day"] = WEEKDAYS.get(datetime.now().weekday())
        context["class"] = Class.objects.filter(category="Putri")
        context["type"] = "putri"
        return context
    
    
class ScheduleListView(BaseAuthorizedModelView, BaseModelDateBasedListView):
    model = Schedule
    queryset = Schedule.objects.select_related("schedule_course", "schedule_course__teacher", "schedule_course__course", "schedule_class", "schedule_time")
    menu_name = 'schedule'
    permission_required = 'schedules.view_schedule'
    paginate_by = 50

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        classes = Class.objects.all()
        context.update({"classes": classes})
        return context


class ScheduleSearchView(BaseAuthorizedModelView, BaseModelDateBasedListView):
    model = Schedule
    queryset = Schedule.objects.select_related("schedule_course", "schedule_course__teacher", "schedule_course__course", "schedule_class", "schedule_time")
    menu_name = 'schedule'
    permission_required = 'schedules.view_schedule'
    template_name = 'schedules/schedule_list.html'

    def get_queryset(self) -> QuerySet[Any]:
        query_class = self.request.GET.get('query_class')
        query_day = self.request.GET.get('query_day')
        query_time = self.request.GET.get('query_time')
        if query_class or query_day or query_time:
            return super().get_queryset()
        else:
            return None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update({"search": True})
        return context

class ScheduleDetailView(BaseAuthorizedModelView, DetailView):
    model = Schedule
    menu_name = 'schedule'
    permission_required = 'schedules.view_schedule'
    raise_exception = False


class ScheduleCreateView(BaseAuthorizedFormView, CreateView):
    model = Schedule
    menu_name = 'schedule'
    form_class = ScheduleForm
    permission_required = 'schedules.add_schedule'
    success_message = "Input data berhasil!"
    error_message = "Input data ditolak!"
    success_url = reverse_lazy("schedule-list")

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        Schedule.objects.update_or_create(
            schedule_day = form.cleaned_data["schedule_day"],
            schedule_time = form.cleaned_data["schedule_time"],
            schedule_class = form.cleaned_data["schedule_class"],
            defaults=dict(
                schedule_course = form.cleaned_data["schedule_course"],
            )
        )
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.success_url)


class ScheduleUpdateView(BaseAuthorizedFormView, UpdateView):
    model = Schedule
    menu_name = 'schedule'
    form_class = ScheduleForm
    permission_required = 'schedules.change_schedule'
    success_message = "Update data berhasil!"
    error_message = "Update data ditolak!"


class ScheduleDeleteView(BaseModelDeleteView):
    model = Schedule
    menu_name = 'schedule'
    permission_required = 'schedules.delete_schedule'
    success_url = reverse_lazy("schedule-list")


class ScheduleUploadView(BaseModelUploadView):
    template_name = 'schedules/schedule_form.html'
    menu_name = "schedule"
    permission_required = 'schedules.add_schedule'
    success_url = reverse_lazy("schedule-list")
    model_class = Schedule


class ScheduleDownloadExcelView(ModelDownloadExcelView):
    menu_name = 'schedule'
    permission_required = 'schedules.view_schedule'
    template_name = 'schedules/download.html'
    header_names = ['No', 'HARI', 'JAM KE-', 'KELAS', 'PELAJARAN', 'PENGAJAR']
    filename = 'DATA JADWAL GURU SMA IT Al Binaa.xlsx'
    queryset = Schedule.objects.select_related("schedule_course", "schedule_course__teacher", "schedule_course__course", "schedule_class", "schedule_time")


class PeriodUploadView(BaseModelUploadView):
    template_name = 'schedules/schedule_form.html'
    menu_name = "period"
    permission_required = 'schedules.add_period'
    success_url = reverse_lazy("schedule-list")
    model_class = Period

def timetable_view(request):
    """
    This view fetches and displays the generated timetable in a grid format.
    """
    # Get all unique classes, periods, and the days of the week
    classes = Class.objects.filter(category="Putra")
    periods = Schedule.objects.values("schedule_time", "time_start", "time_end").order_by('schedule_time').distinct()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday", "Sunday"]

    # You can select a class to view its specific timetable
    selected_class_id = request.GET.get('class_id')
    
    if selected_class_id:
        # Filter entries for the selected class
        schedule_entries = Schedule.objects.filter(schedule_class_id=selected_class_id, schedule_course__type="putra").select_related('schedule_course', 'schedule_class')
        selected_class = Class.objects.get(id=selected_class_id)
    else:
        # By default, show the first class or an empty schedule
        if classes.exists():
            selected_class = classes.first()
            schedule_entries = Schedule.objects.filter(lesson__class_assigned=selected_class, schedule_course__type="putra").select_related('schedule_course__teacher', 'schedule_course__course_name')
        else:
            selected_class = None
            schedule_entries = Schedule.objects.none()

    # Structure the data for easy rendering in the template
    # The grid will be a dictionary: {(day, period_number): "Subject by Teacher in Room", ...}
    schedule_grid = {}
    for entry in schedule_entries:
        key = (entry.schedule_day, entry.schedule_time)
        schedule_grid[key] = f"{entry.schedule_course.course_name}<br><small>{entry.schedule_course.teacher.teacher_name}<br>({entry.schedule_class.class_name})</small>"

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'periods': periods,
        'days': days,
        'schedule_grid': schedule_grid,
    }
    return render(request, 'schedules/timetable.html', context)

def generate_timetable_view(request):
    """
    This view triggers the timetable generation command.
    """
    if request.method == 'POST':
        try:
            # Call the management command programmatically
            call_command('generatetimetable')
            messages.success(request, 'Successfully generated a new timetable!')
        except Exception as e:
            # Catch potential errors during generation
            messages.error(request, f'An error occurred during timetable generation: {e}')
        
        # Redirect back to the timetable display page
        return redirect('timetable_view')
    
    # If not a POST request, just redirect
    return redirect('timetable_view')