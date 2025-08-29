# utils/mixins.py
from datetime import datetime
from io import BytesIO
from django.contrib import messages as django_messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.db.models import Q, Model, Count
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import FileResponse, HttpRequest, HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView
from pandas import read_excel
from typing import Any
from classes.models import Class
from courses.models import Course, Subject
from reports.forms import ReportFormV2, ReportUpdatePetugasForm
from reports.models import Report
from schedules.models import Period, ReporterSchedule, Schedule
from userlog.models import UserLog
from users.models import Teacher
from utils.forms import UploadModelForm
from utils.menu_link import export_menu_link
from xlsxwriter import Workbook
from utils_piket.validate_datetime import get_day, parse_to_date
from utils_piket.whatsapp_albinaa import send_whatsapp_action, send_whatsapp_group, send_whatsapp_report
import calendar


# KELAS DEFAULT UNTUK HALAMAN WAJIB LOGIN DAN PERMISSION
class BaseAuthorizedModelView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Base view for generic model views with shared functionality."""
    raise_exception = False  # Raise PermissionDenied for unauthorized users
    menu_name = ''
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Shared method to enrich context data."""
        data = super().get_context_data(**kwargs)
        model_name = self.kwargs.get("site_title", "").split(" - ")[0].title()
        data.update(self.kwargs)
        data.update({"form_name": model_name})
        data.update(export_menu_link(f"{self.menu_name}"))
        return data

# KELAS DEFAULT UNTUK HALAMAN FORM CREATE DAN UPDATE
class BaseAuthorizedFormView(BaseAuthorizedModelView):
    """Base view for form-based views like CreateView and UpdateView."""
    success_message: str = "Input data berhasil!"
    error_message: str = "Gagal input. Ada sesuatu yang salah!"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        django_messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        django_messages.error(self.request, self.error_message)
        return super().form_invalid(form)


# KELAS DEFAULT UNTUK HALAMAN FORM DELETE
class BaseModelDeleteView(BaseAuthorizedModelView, DeleteView):
    """Base view for DeleteView."""
    success_message: str = "Data berhasil dihapus!"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        django_messages.success(self.request, self.success_message)
        return super().post(request, *args, **kwargs)


# KELAS DEFAULT UNTUK HALAMAN YANG MENGGUNAKAN QUERY DI LISTVIEW
class BaseModelQueryListView(ListView):
    """Base view for generic model views with shared functionality."""
    model = None
    
    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get("query")
        if query:
            match self.model.__qualname__:
                case "Class":
                    queryset = self.model.objects.filter(Q(class_name__icontains=query) | Q(short_class_name__icontains=query))
                    return queryset
                case "Course":
                    queryset = self.model.objects.select_related("teacher").filter(Q(course_name__icontains=query) | Q(course_code__icontains=query) | Q(category__icontains=query) | Q(teacher__teacher_name__icontains=query))
                    return queryset
                case "User":
                    queryset = self.model.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
                    return queryset
                case _:
                    raise Http404("Model dalam ListView tidak ditemukan!")
        return super().get_queryset()
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get('query')
        return context


# KELAS DEFAULT UNTUK HALAMAN YANG MENGGUNAKAN QUERY KOMPLEKS BERTANGGAL DI LISTVIEW
class BaseModelDateBasedListView(ListView):
    """Base view for generic model views with shared functionality."""
    model = None
    
    def get_queryset(self) -> QuerySet[Any]:
        query_class = self.request.GET.get('query_class') if self.request.GET.get('query_class') else None
        query_day = self.request.GET.get('query_day') if self.request.GET.get('query_day') else None
        query_time = self.request.GET.get('query_time') if self.request.GET.get('query_time') else None
        query_date = self.request.GET.get('query_date')

        valid_date = parse_to_date(query_date)
        
        if query_day and query_class and query_time:
            return self.queryset.filter(schedule_day=query_day, schedule_class__class_name=query_class, schedule_time=query_time)
        elif query_time and query_class:
            match self.model.__qualname__:
                case "Schedule":
                    return self.queryset.filter(schedule_class__class_name=query_class, schedule_time=query_time)
                case "Report":
                    return self.queryset.filter(report_date=valid_date, schedule__schedule_class__class_name=query_class, schedule__schedule_time=query_time)
        elif query_class and query_day:
            return self.queryset.filter(schedule_day=query_day, schedule_class__class_name=query_class)
        elif query_day and query_time:
            return self.queryset.filter(schedule_day=query_day, schedule_time=query_time)
        elif query_day:
            return self.queryset.filter(schedule_day=query_day)
        elif query_class:
            match self.model.__qualname__:
                case "Schedule":
                    return self.queryset.filter(schedule_class__class_name=query_class)
                case "Report":
                    return self.queryset.filter(report_date=valid_date, schedule__schedule_class__class_name=query_class)
        elif query_time:
            match self.model.__qualname__:
                case "Schedule":
                    return self.queryset.filter(schedule_time=query_time)
                case "Report":
                    return self.queryset.filter(report_date=valid_date, schedule__schedule_time=query_time)
            
        return super().get_queryset()
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query_class"] = self.request.GET.get('query_class') if self.request.GET.get('query_class') else None
        context["query_date"] = self.request.GET.get('query_date') if self.request.GET.get('query_date') else str(datetime.now().date())
        context["query_day"] = self.request.GET.get('query_day') if self.request.GET.get('query_day') else None
        context["query_time"] = self.request.GET.get('query_time') if self.request.GET.get('query_time') else None
        return context


# KELAS DEFAULT UNTUK HALAMAN UPLOAD EXCEL KE DATABASE
class BaseModelUploadView(BaseAuthorizedModelView, FormView):
    """Base view for generic model views with shared functionality."""
    form_class = UploadModelForm
    success_message: str = "Upload completed successfully!"
    error_message: str = "Upload failed!"
    model_class = None

    def process_excel_data(self, model_name: Model, file: str):
        """Process the uploaded Excel file and update or create Class instances."""
        start_id = 1
        df = read_excel(
                file,
                na_filter=False,
            )
        row, _ = df.shape
        for i in range(row):
            match model_name.__qualname__:
                case "Class":
                    model_name.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        class_name = df.iloc[i, 1],
                        defaults={
                            "short_class_name": df.iloc[i, 2],
                            "category": df.iloc[i, 3],
                        },
                    )
                case "Subject":
                    model_name.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        name = df.iloc[i, 1],
                        defaults={
                            "short_name": df.iloc[i, 2],
                            "category": df.iloc[i, 4],
                            "type": df.iloc[i, 5],
                            "status": df.iloc[i, 6],
                        },
                    )
                case "Period":
                    model_name.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        number = df.iloc[i, 1],
                        defaults={
                            "time_start": df.iloc[i, 2],
                            "time_end": df.iloc[i, 3],
                            "short_time_start": df.iloc[i, 4],
                            "short_time_end": df.iloc[i, 5],
                            "type": df.iloc[i, 6],
                        },
                    )
                case "Course":
                    subject = get_object_or_404(Subject, id=df.iloc[i, 2])
                    teacher = get_object_or_404(Teacher, id=df.iloc[i, 3])
                    if df.iloc[i, 5]:
                        class_obj = get_object_or_404(Class, id=df.iloc[i, 5])
                    else:
                        class_obj = None
                    model_name.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        course = subject,
                        course_code = df.iloc[i, 1],
                        defaults={
                            "course_code": df.iloc[i, 1],
                            "teacher": teacher,
                            "type": df.iloc[i, 4],
                            "class_assigned": class_obj if class_obj else None,
                            "periods_per_week": df.iloc[i, 6] if df.iloc[i, 6] else 1,
                            "consecutive_periods_needed": df.iloc[i, 7] if df.iloc[i, 7] else 1,
                        },
                    )

                case "Schedule":
                    class_names = Class.objects.filter(category=df.iloc[i, 18])
                    period = get_object_or_404(Period, id=df.iloc[i, 1])
                    for index, class_name in enumerate(class_names, start=2):
                        course = Course.objects.select_related("teacher", "class_assigned", "course").get(course_code=df.iloc[i, index])
                        model_name.objects.update_or_create(
                            pk = start_id,
                            schedule_day = df.iloc[i, 0],
                            schedule_time = period,
                            schedule_class = class_name,
                            defaults={
                                "schedule_course": course,
                                "type": df.iloc[i, 18],
                            },
                        )
                        start_id += 1
                case "ReporterSchedule":
                    if df.iloc[i, 3]:
                        teacher = get_object_or_404(Teacher, id=df.iloc[i, 3])
                    else:
                        teacher = None
                    model_name.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        defaults={
                            "schedule_day": df.iloc[i, 1],
                            "schedule_time": df.iloc[i, 2],
                            "reporter": teacher,
                            "time_start": df.iloc[i, 4],
                            "time_end": df.iloc[i, 5],
                            "type": df.iloc[i, 6],
                        },
                    )
                case "User":
                    if df.iloc[i, 8]:
                        group = get_object_or_404(Group, pk=df.iloc[i, 8])
                    obj, is_created = User.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        username = df.iloc[i, 1],
                        defaults={
                            "first_name": df.iloc[i, 3],
                            "last_name": df.iloc[i, 4],
                            "email": df.iloc[i, 5],
                            "is_staff": True if df.iloc[i, 6] else False,
                            "is_superuser": True if df.iloc[i, 7] else False,
                        },
                    )
                    Teacher.objects.update_or_create(
                        user = obj,
                        defaults = {
                            "teacher_name": df.iloc[i, 3],
                            "short_name": df.iloc[i, 3],
                            "email": df.iloc[i, 5],
                            "gender": df.iloc[i, 10],
                        },
                    )
                    if is_created:
                        obj.set_password(df.iloc[i, 2])
                        obj.save()
                    if df.iloc[i, 8]:
                        obj.groups.add(group)
                case _:
                    print("Error Case!")
                    
    
    def form_valid(self, form: Any) -> HttpResponse:
        try:
            if self.model_class is None: raise Http404("Model tidak ditemukan!")
            self.process_excel_data(self.model_class, form.cleaned_data["file"])
            django_messages.success(self.request, self.success_message)
            return super().form_valid(form)
        except IntegrityError as e:
            self.error_message = f"Upload data sudah terbaru! Note: {str(e)}"
            django_messages.error(self.request, self.error_message)
            return super().form_invalid(form)
        except Exception as e:
            self.error_message = f"Upload data ditolak! Error: {str(e)}"
            django_messages.error(self.request, self.error_message)
            return super().form_invalid(form)



class ModelDownloadExcelView(BaseAuthorizedModelView):
    header_names = []
    filename = ''
    queryset = None
    individual = None

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, self.header_names)
        tercapai_format = workbook.add_format({
            "fg_color": "green",
        })
        tidak_tercapai_format = workbook.add_format({
            "fg_color": "red",
        })
        row = 2
        
        if self.individual:
            worksheet.write(row, 0, self.teacher)
            worksheet.write(row, 1, f'{calendar.month_name[self.month]} {self.year}')
            for tanggal, data in self.queryset.items():
                worksheet.write(row, 0, row)
                worksheet.write(row, 1, f"{tanggal}")
                col = 2
                for jam in range(1, 10):
                    if jam in data:
                        worksheet.write(row, col, data[jam])
                    else:
                        worksheet.write(row, col, "-")
                    col += 1
                worksheet.write(row, col, data["Sum"])
                row += 1
            worksheet.merge_range(row, 0, row, col-1, "TOTAL JAM")
            worksheet.write(row, col, self.total_jam)
            worksheet.autofit()
            workbook.close()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename=self.filename)

        for data in (self.queryset or [{"data": "Error!"}]):
            if self.menu_name == 'class':
                worksheet.write_row(row, 0, [row, f"{data.class_name}", f"{data.short_class_name}"])
            elif self.menu_name == 'course':
                worksheet.write_row(row, 0, [row, f"{data.course_name}", f"{data.course_code}", f"{data.teacher.teacher_name} {data.teacher.teacher_name}"])
            elif self.menu_name == 'report':
                subtitute_teacher = f"{data.subtitute_teacher.teacher_name}" if data.subtitute_teacher else ""
                reporter = f"{data.reporter.teacher_name}" if data.reporter else ""
                worksheet.write_row(row, 0, [row, f"{data.report_date}", f"{data.report_day}", data.status, data.schedule.schedule_time.number, f"{data.schedule.schedule_class}", f"{data.schedule.schedule_course.course.name}",
                                         f"{data.schedule.schedule_course.teacher.teacher_name}", subtitute_teacher, reporter])
            elif self.menu_name == 'schedule':
                worksheet.write_row(row, 0, [row, f"{data.schedule_day}", f"{data.schedule_time}", data.schedule_class.class_name, data.schedule_course.course_name, 
                                         f"{data.schedule_course.teacher.teacher_name} {data.schedule_course.teacher.teacher_name}"])
            elif self.menu_name == 'reporter-schedule':
                reporter = data.reporter.teacher_name if data.reporter else data.reporter
                worksheet.write_row(row, 0, [row, f"{data.schedule_day}", f"{data.schedule_time}", 
                                         f"{reporter}", f"{data.time_start}", f"{data.time_end}"])
            elif self.menu_name == 'user':
                worksheet.write_row(row, 0, [row, data.username, 'Albinaa2004', data.password, data.email, f"{data.is_staff}", f"{data.is_active}",
                                         f'{data.is_superuser}', f"{data.date_joined}", f"{data.last_login}"])
            elif self.menu_name == 'Tilawah':
                if data.tercapai:
                    worksheet.write_row(row, 0, [row, data.santri.nis, data.santri.student_name, data.santri.student_class.class_name, data.tercapai, data.target, data.halaman, data.surat, data.ayat,
                                         data.tajwid, data.kelancaran, data.catatan], cell_format=tercapai_format)
                else:
                    worksheet.write_row(row, 0, [row, data.santri.nis, data.santri.student_name, data.santri.student_class.class_name, data.tercapai, data.target, data.halaman, data.surat, data.ayat,
                                         data.tajwid, data.kelancaran, data.catatan], cell_format=tidak_tercapai_format)

            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=self.filename)

class QuickReportMixin(BaseAuthorizedModelView, ListView):
    class_name = []
    grouped_report_data = []
    type = "putra"

    def find_and_create_reports(self, valid_date_query: Any, time: Any) -> QuerySet[Any]:
        data = self.queryset.filter(report_date=valid_date_query, schedule__schedule_time=time, schedule__type=self.type)\
                                    .values("id", "status", "reporter__short_name", "schedule__schedule_class", "schedule__schedule_time__time_start", "schedule__schedule_time__time_end",
                                            "schedule__schedule_course__teacher__short_name",
                                            "schedule__schedule_course__course__short_name").order_by('schedule__schedule_class__class_name')
        if (self.type == "putra" and len(data) == len(self.class_name)) or (self.type == "putri" and len(data) == len(self.class_name)):
            self.grouped_report_data.append(data)
        else:
            self.create_report_objects(valid_date_query, time)
    
    def create_report_objects(self, valid_query_date: Any, schedule_time: Any) -> bool:
        # Cari data jadwal di hari sesuai query dan di waktu jam 1 sampai  9
        schedule_list = Schedule.objects.select_related("schedule_course", "schedule_course__teacher", "schedule_class") \
                                .filter(schedule_day=get_day(valid_query_date), schedule_time=schedule_time, type=self.type)
        try:
            reporter_schedule = ReporterSchedule.objects.select_related("reporter").get(schedule_day=get_day(valid_query_date), schedule_time=schedule_time, type=self.type)
        except:
            reporter_schedule = None
        # Jika tidak ditemukan, maka nilai False
        if (self.type == "putra" and len(schedule_list) == len(self.class_name)) or (self.type == "putri" and len(schedule_list) == len(self.class_name)):
            # Jika ditemukan, maka buat laporan dengan jadwal dimasukkan satu per satu
            for schedule in schedule_list:
                report_data = self.queryset.filter(report_date=valid_query_date, schedule=schedule, type=self.type)
                if len(report_data) > 1:
                    report_data.first().delete()
                obj, is_created = Report.objects.update_or_create(
                    report_date = valid_query_date,
                    schedule = schedule,
                    # reporter = reporter_schedule.reporter,
                    defaults={
                        'reporter': reporter_schedule.reporter,
                        'type': self.type
                    }
                )
            return True
        return False

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        query_date = self.request.GET.get('query_date', datetime.now().date())
        valid_date = parse_to_date(query_date)
        day = get_day(valid_date)
        self.grouped_report_data = []
        if self.type=="putra" and day == "Ahad":
            for i in range(1, 8):
                self.find_and_create_reports(valid_date, i)

                
        elif self.type=="putri" or day != "Jumat":
            for i in range(1, 10):
                self.find_and_create_reports(valid_date, i)

        
        context = super().get_context_data(**kwargs)
        context["grouped_report_data"] = self.grouped_report_data
        context["class"] = self.class_name
        context["teachers"] = Teacher.objects.select_related('user').all()
        query_date = self.request.GET.get('query_date', str(datetime.now().date()))
        context["query_date"] = query_date
        context["type"] = self.type
        return context
    

class ReportUpdateReporterMixin(BaseAuthorizedFormView, FormView):
    model = Report
    menu_name = 'report'
    form_class = ReportUpdatePetugasForm
    template_name = 'reports/report_form.html'
    permission_required = 'reports.change_report'
    success_message = "Update data berhasil!"
    error_message = "Update data ditolak!"
    redirect_url = "report-quick-create-v2"

    def get_form_kwargs(self) -> dict[str, Any]:
        data = super().get_form_kwargs()
        data["report_date"] = self.kwargs.get("date")
        data["schedule_time"] = self.kwargs.get("pk")
        return data

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        reporter_name = form.cleaned_data["reporter"]
        report_date = self.kwargs.get("date")
        schedule_time = self.kwargs.get("pk")
        reports = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher", "reporter")\
                                    .filter(report_date=report_date, schedule__schedule_time=schedule_time)
        if reporter_name:
            reports.update(reporter=reporter_name.id)
        else:
            reports.update(reporter=None)
        redirect_url = reverse(self.redirect_url)
        query_params = f'?query_date={report_date}'
        django_messages.success(self.request, self.success_message)
        return redirect(redirect_url + query_params)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["reporter"] = True
        context["date"] = self.kwargs.get("date")
        context["time"] = self.kwargs.get("pk")
        return context
    

class ReportUpdateQuickViewMixin(BaseAuthorizedFormView, UpdateView):
    model = Report
    menu_name = 'report'
    form_class = ReportFormV2
    permission_required = 'reports.change_report'
    success_message = "Update data berhasil!"
    error_message = "Update data ditolak!"
    redirect_url = "report-quick-create-v2"
    app_name = "QUICK REPORT V2"


    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        object = self.get_object()
        status = form.cleaned_data["status"]
        reporter = ''
        if object.reporter:
            reporter = object.reporter.teacher_name

        message = f"laporan piket {object.report_day} {object.report_date} Jam ke-{object.schedule.schedule_time} {object.schedule.schedule_course} dengan status {status}"
        UserLog.objects.create(
            user = reporter or  self.request.user.teacher_name,
            action_flag = "mengubah",
            app = self.app_name,
            message = message,
        )
        redirect_url = reverse(self.redirect_url)
        query_params = f'?query_date={object.report_date}'
        self.object = form.save()
        django_messages.success(self.request, self.success_message)
        return redirect(redirect_url + query_params)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_object()
        return context
    


class SubmitViewMixins(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    type = ""

    def form_valid(self, form: Any) -> HttpResponse:
        report_date = form.cleaned_data['date_string']
        schedule_time = form.cleaned_data['time_string']

        reports = self.queryset.filter(report_date=report_date, schedule__schedule_time=schedule_time, schedule__type=self.type, type=self.type)
        reports.update(is_submitted=True)
        rep = reports.values_list("status", flat=True)
        if "Sakit" in rep or "Izin" in rep or "Tanpa Keterangan" in rep:
            reports.update(is_complete=False)
        else:
            reports.update(is_complete=True)

        # Filter and order the queryset
        qs = self.queryset.filter(report_date=report_date, type=self.type).order_by('schedule__schedule_time', 'schedule__schedule_class')
        # reporter_schedule = ReporterSchedule.objects.filter(schedule_day=get_day(report_date))


        total_time = 10
        if get_day(report_date) == "Ahad":
            total_time = 8

        # Initialize the grouped data list
        grouped_data = []

        # Initialize a dictionary to group reports by schedule_time
        grouped_dict = {}

        # Group the reports by schedule_time
        for report in qs:
            schedule_time = int(report.schedule.schedule_time.number)
            is_complete = report.is_complete
            # is_submitted = report.is_submitted
            status = report.status
            if schedule_time not in grouped_dict:
                grouped_dict[schedule_time] = []
            elif not is_complete and status != "Hadir":
                grouped_dict[schedule_time].append(report)
            elif is_complete:
                grouped_dict[schedule_time] = [report]

        # Create the grouped_data list based on the schedule_time
        for time_num in range(1, total_time):  # Assuming schedule_time ranges from 1 to 9
            if time_num in grouped_dict:
                grouped_data.append(grouped_dict[time_num])
            else:
                grouped_data.append([])

        messages = f'''*[LAPORAN KETIDAKHADIRAN GURU DALAM KBM]*
*TIM PIKET SMAS IT AL BINAA*
Hari: {get_day(report_date)}, {qs.first().report_date.strftime("%d %B %Y") if qs.exists() else datetime.now().date().strftime("%d %B %Y")}
Pukul: {datetime.now().time().strftime("%H:%M:%S")} WIB

'''
        for index_outer in range(len(grouped_data)):
            inner_data_length = len(grouped_data[index_outer])
            if inner_data_length > 0:
                for inner_index in range(inner_data_length):
                    if grouped_data[index_outer][inner_index].is_complete:
                        messages += f"Jam ke {index_outer+1} ✅ LENGKAP\n"
                    elif inner_index == 0 and not grouped_data[index_outer][inner_index].is_complete:
                        messages += f"Jam ke {index_outer+1} ✅\n"
                        messages += f'''
KELAS {grouped_data[index_outer][inner_index].schedule.schedule_class}
{grouped_data[index_outer][inner_index].schedule.schedule_course}
Keterangan : {grouped_data[index_outer][inner_index].status}
Pengganti : {grouped_data[index_outer][inner_index].subtitute_teacher.teacher_name if grouped_data[index_outer][inner_index].subtitute_teacher else "-"}
Catatan : {grouped_data[index_outer][inner_index].notes or "-"}
'''
                        
                    elif inner_index != 0 and not grouped_data[index_outer][inner_index].is_complete:
                        messages += f'''
KELAS {grouped_data[index_outer][inner_index].schedule.schedule_class}
{grouped_data[index_outer][inner_index].schedule.schedule_course}
Keterangan : {grouped_data[index_outer][inner_index].status}
Pengganti : {grouped_data[index_outer][inner_index].subtitute_teacher.teacher_name if grouped_data[index_outer][inner_index].subtitute_teacher else "-"}
Catatan : {grouped_data[index_outer][inner_index].notes or "-"}
'''
                    if inner_index == inner_data_length-1:
                        messages += f'\nPetugas Piket: {grouped_data[index_outer][inner_index].reporter.teacher_name if grouped_data[index_outer][inner_index].reporter else "-"}\n'
                        messages += '--------------------------\n\n'
            else:
                messages += f"Jam ke {index_outer+1}\n"

        send_whatsapp_group(messages)
        if self.type == "putra":
            simplified_message = f'''📹📹📹 *PIKET SMA* 📹📹📹

        *{reports[0].report_day}, {report_date}*
        KBM *Jam ke-{form.cleaned_data["time_string"]}*

10-A {"✅        " if reports[0].subtitute_teacher or reports[0].status == "Hadir" else "⚠️ (" + reports[0].status + ")"}11-A {"✅        " if reports[6].subtitute_teacher or reports[6].status == "Hadir" else "⚠️ (" + reports[6].status + ")"}12-A {"✅        " if reports[11].subtitute_teacher or reports[11].status == "Hadir" else "⚠️ (" + reports[11].status + ")"}
10-B {"✅        " if reports[1].subtitute_teacher or reports[1].status == "Hadir" else "⚠️ (" + reports[1].status + ")"}11-B {"✅        " if reports[7].subtitute_teacher or reports[7].status == "Hadir" else "⚠️ (" + reports[7].status + ")"}12-B {"✅        " if reports[12].subtitute_teacher or reports[12].status == "Hadir" else "⚠️ (" + reports[12].status + ")"}
10-C {"✅        " if reports[2].subtitute_teacher or reports[2].status == "Hadir" else "⚠️ (" + reports[2].status + ")"}11-C {"✅        " if reports[8].subtitute_teacher or reports[8].status == "Hadir" else "⚠️ (" + reports[8].status + ")"}12-C {"✅        " if reports[13].subtitute_teacher or reports[13].status == "Hadir" else "⚠️ (" + reports[13].status + ")"}
10-D {"✅        " if reports[3].subtitute_teacher or reports[3].status == "Hadir" else "⚠️ (" + reports[3].status + ")"}11-D {"✅        " if reports[9].subtitute_teacher or reports[9].status == "Hadir" else "⚠️ (" + reports[9].status + ")"}12-D {"✅        " if reports[14].subtitute_teacher or reports[14].status == "Hadir" else "⚠️ (" + reports[14].status + ")"}
10-E  {"✅        " if reports[4].subtitute_teacher or reports[4].status == "Hadir" else "⚠️ (" + reports[4].status + ")"}11-E  {"✅        " if reports[10].subtitute_teacher or reports[10].status == "Hadir" else "⚠️ (" + reports[10].status + ")"}12-E {"✅        " if reports[15].subtitute_teacher or reports[15].status == "Hadir" else "⚠️ (" + reports[15].status + ")"}
10-F  {"✅        " if reports[5].subtitute_teacher or reports[5].status == "Hadir" else "⚠️ (" + reports[5].status + ")"}

Petugas: *{reports[0].reporter.teacher_name}*
🎦🎦🎦🎦🎦🎦🎦🎦🎦🎦'''
        else:
            simplified_message = f'''📹📹📹 *PIKET SMA* 📹📹📹

        *{reports[0].report_day}, {report_date}*
        KBM *Jam ke-{form.cleaned_data["time_string"]}*

10-G {"✅        " if reports[0].subtitute_teacher or reports[0].status == "Hadir" else "⚠️ (" + reports[0].status + ")"}11-F {"✅        " if reports[3].subtitute_teacher or reports[3].status == "Hadir" else "⚠️ (" + reports[3].status + ")"}12-F {"✅        " if reports[6].subtitute_teacher or reports[6].status == "Hadir" else "⚠️ (" + reports[6].status + ")"}
10-H {"✅        " if reports[1].subtitute_teacher or reports[1].status == "Hadir" else "⚠️ (" + reports[1].status + ")"}11-G {"✅        " if reports[4].subtitute_teacher or reports[4].status == "Hadir" else "⚠️ (" + reports[4].status + ")"}12-G {"✅        " if reports[7].subtitute_teacher or reports[7].status == "Hadir" else "⚠️ (" + reports[7].status + ")"}
10-I {"✅        " if reports[2].subtitute_teacher or reports[2].status == "Hadir" else "⚠️ (" + reports[2].status + ")"}11-H {"✅        " if reports[5].subtitute_teacher or reports[5].status == "Hadir" else "⚠️ (" + reports[5].status + ")"}12-H {"✅        " if reports[8].subtitute_teacher or reports[8].status == "Hadir" else "⚠️ (" + reports[8].status + ")"}

Petugas: *{reports[0].reporter.teacher_name}*
🎦🎦🎦🎦🎦🎦🎦🎦🎦🎦'''
        send_whatsapp_group(simplified_message)
        django_messages.success(request=self.request, message="Submit Data Berhasil!")
        query_params = f'?query_date={report_date}'
        return HttpResponseRedirect(reverse("report-quick-create-v3") + query_params)
    

class TeacherRecapMixins(BaseAuthorizedModelView, BaseModelQueryListView):
    type = "putra"
    
    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')

        if date_start and date_end:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
                                .exclude(schedule__schedule_course__course_code__in=["APE", "TKL", "APEN3"])\
                                .filter(report_date__gte=date_start, report_date__lte=date_end, type=self.type)\
                                .values('schedule__schedule_course__teacher','schedule__schedule_course__teacher__teacher_name')\
                                .annotate(
                                    hadir_count=Count('status',  filter=Q(status="Hadir")),
                                    izin_count=Count('status',  filter=Q(status="Izin")),
                                    sakit_count=Count('status',  filter=Q(status="Sakit")),
                                    alpha_count=Count('status',  filter=Q(status="Tanpa Keterangan")),
                                    all_count=Count('status'),
                                    )\
                                .distinct().order_by()
        else:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
                                .exclude(schedule__schedule_course__course_code__in=["APE", "TKL", "APEN3"])\
                                .filter(report_date__month=datetime.now().month, report_date__year=datetime.now().year, type=self.type)\
                                .values('schedule__schedule_course__teacher','schedule__schedule_course__teacher__teacher_name')\
                                .annotate(
                                    hadir_count=Count('status',  filter=Q(status="Hadir")),
                                    izin_count=Count('status',  filter=Q(status="Izin")),
                                    sakit_count=Count('status',  filter=Q(status="Sakit")),
                                    alpha_count=Count('status',  filter=Q(status="Tanpa Keterangan")),
                                    all_count=Count('status'),
                                    )\
                                .distinct().order_by()


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        this_year = datetime.now().year
        this_month = datetime.now().month
        last_day_of_month = calendar.monthrange(this_year, this_month)[1]

        if date_start and date_end:
            context["date_start"] = datetime.strptime(date_start, "%Y-%m-%d")
            context["date_end"] = datetime.strptime(date_end, "%Y-%m-%d")
        else:
            context["date_start"] = datetime.strptime(f"{this_year}-{this_month}-1", "%Y-%m-%d")
            context["date_end"] = datetime.strptime(f"{this_year}-{this_month}-{last_day_of_month}", "%Y-%m-%d")

        context["date_start_str"] = date_start
        context["date_end_str"] = date_end
        return context