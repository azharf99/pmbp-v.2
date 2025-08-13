# utils/mixins.py
from datetime import datetime
from io import BytesIO
import re
import string
from django.conf import settings
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
from pandas import read_csv, read_excel
from typing import Any
from alumni.models import Alumni
from classes.models import Class
from courses.models import Course, Subject
from extracurriculars.models import Extracurricular
from files.forms import FileForm
from prestasi.models import Prestasi
from reports.forms import ReportFormV2, ReportUpdatePetugasForm
from reports.models import Report
from schedules.models import Period, ReporterSchedule, Schedule
from userlog.models import UserLog
from users.models import Teacher
from utils.forms import UploadModelForm
from utils.menu_link import export_menu_link
from xlsxwriter import Workbook
from utils_humas.whatsapp_albinaa import send_WA_create_update_delete, send_WA_general
from utils_piket.validate_datetime import get_day, parse_to_date
from utils_piket.whatsapp_albinaa import send_whatsapp_action, send_whatsapp_group, send_whatsapp_report
import calendar


class SendSuccessMessageLogAndWhatsapp:
    request = ''
    success_message = ''
    teacher = ''
    teacher_phone = ''
    action_flag = ''
    app = ''
    app_link = ''
    object_name = ''
    custom_message = ''
    def __init__(self, request, object_name, success_message = '', action_flag='', app='', app_link='', custom_message='') -> None:
        self.request = request
        self.success_message = success_message
        self.teacher = self.request.user.teacher
        self.teacher_phone = self.teacher.phone
        self.action_flag = action_flag
        self.object_name = object_name
        self.app = app
        self.app_link = app_link
        self.custom_message = custom_message

    def send(self):
        django_messages.success(self.request, self.success_message)
        UserLog.objects.create(
                user=self.teacher,
                action_flag=self.action_flag.upper(),
                app=self.app.upper(),
                message=self.custom_message if self.custom_message else f"berhasil {self.action_flag} data {self.app} {self.object_name}"
        )
        send_WA_create_update_delete(self.teacher_phone or '085701570100', self.action_flag, f'{self.app} {self.object_name}', f'{self.app_link}/', f'detail/{self.object_name.id}/')


class TitleView(View):
    title_of_table = ''
    form_link = ''
    link_name = ''
    form_name = ''

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Shared method to enrich context data."""
        context = super().get_context_data(**kwargs)
        title_for_display = self.kwargs.get("site_title", "").split(" - ")[0]
        context.update(self.kwargs)
        context.update({"form_name": title_for_display})
        context.update({"form_link": self.form_link})
        context.update({"link_name": self.link_name})
        context.update({"title_of_table": self.title_of_table})
        context.update({"title_for_display": title_for_display})
        return context

class LinkView(View):
    links = []

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Shared method to enrich context data."""
        context = super().get_context_data(**kwargs)
        if not self.links:
            model_name = re.sub(r'^([^A-Z]*[A-Z][^A-Z]*)([A-Z])', r'\1-\2', self.model.__name__).lower()
            links = [f'{model_name}-list',f'{model_name}-detail', f'{model_name}-update', f'{model_name}-delete', f'{model_name}-download']
            self.links = links
        context["link_current_view"], context["link_detail"], context["link_update"], context["link_delete"], context["link_download"] = self.links
        return context


class SearchView(View):
    action_target_url_name = ''
    placeholder = 'Ketik disini...'
    query, query_class, query_time, query_day, query_date, month, year = '', '', '', '', '', '', ''

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Shared method to enrich context data."""
        context = super().get_context_data(**kwargs)
        context["action_target_url_name"] = self.action_target_url_name
        context["placeholder"] = self.placeholder
        context["query"] = self.query
        context["query_class"] = self.query_class
        context["query_time"] = self.query_time
        context["query_day"] = self.query_day
        context["query_date"] = self.query_date
        context["month"] = self.month
        context["year"] = self.year
        return context
    
class TableView(View):
    table_column_names = []

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["table_column_names"] = self.table_column_names
        return context


class BaseLoginRequiredView(LoginRequiredMixin, TitleView):
    """Base view for generic model views with shared functionality."""
    pass


class BaseLoginAndPermissionRequiredView(LoginRequiredMixin, PermissionRequiredMixin, TitleView):
    """Base view for generic model views with shared functionality."""
    raise_exception = False  # Raise PermissionDenied for unauthorized users

# KELAS DEFAULT UNTUK HALAMAN FORM CREATE DAN UPDATE
class BaseLoginAndPermissionFormView(BaseLoginAndPermissionRequiredView, LinkView):
    """Base view for form-based views like CreateView and UpdateView."""
    success_message: str = "Submit data berhasil!"
    error_message: str = "Gagal submit. Ada sesuatu yang salah!"
    

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        app_name, permission = self.permission_required.split(".")
        action_flag, app = permission.split("_")
        message = SendSuccessMessageLogAndWhatsapp(self.request, self.object, self.success_message, action_flag, app, app_name)
        message.send()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        django_messages.error(self.request, self.error_message)
        return super().form_invalid(form)



# KELAS DEFAULT UNTUK HALAMAN FORM DELETE
class BaseLoginAndPermissionModelDeleteView(BaseLoginAndPermissionRequiredView, DeleteView):
    """Base view for DeleteView."""
    success_message: str = "Data berhasil dihapus!"


    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        data = self.get_object()
        app_name, permission = self.permission_required.split(".")
        action_flag, app = permission.split("_")
        message = SendSuccessMessageLogAndWhatsapp(self.request, data, self.success_message, action_flag, app, app_name)
        message.send()
        return super().post(request, *args, **kwargs)


# KELAS DEFAULT UNTUK HALAMAN YANG MENGGUNAKAN QUERY DI LISTVIEW
class BaseQueryListView(ListView):
    """Base view for generic model views with shared functionality."""
    model = None
    
    def get_queryset(self) -> QuerySet[Any]:
        self.query = self.request.GET.get("query")
        if self.query:
            self.paginate_by = None
            model_name = self.model.__qualname__
            if model_name == "Class":
                queryset = self.model.objects.filter(Q(class_name__icontains=self.query) | Q(short_class_name__icontains=self.query))
            elif model_name == "Course":
                queryset = self.model.objects.select_related("teacher").filter(Q(course_name__icontains=self.query) | Q(course_code__icontains=self.query) | Q(category__icontains=self.query) | Q(teacher__first_name__icontains=self.query))
            elif model_name == "User":
                queryset = self.model.objects.filter(Q(first_name__icontains=self.query) | Q(last_name__icontains=self.query) | Q(email__icontains=self.query))
            elif model_name == "Alumni":
                queryset = Alumni.objects.filter(Q(nis__icontains=self.query)|
                                         Q(name__icontains=self.query)|
                                         Q(nisn__icontains=self.query)|
                                         Q(group__icontains=self.query)|
                                         Q(graduate_year__icontains=self.query)|
                                         Q(undergraduate_university__icontains=self.query)|
                                         Q(undergraduate_university_entrance__icontains=self.query)|
                                         Q(undergraduate_department__icontains=self.query))
            elif model_name == "Prestasi":
                if self.kwargs.get("prestasi_active_link"):
                    queryset = Prestasi.objects.filter(Q(awardee__icontains=self.query) | Q(awardee_class__icontains=self.query) | Q(name__icontains=self.query))
                else:
                    queryset = Prestasi.objects.filter(year__gte=settings.TAHUN_AWAL_AJARAN, created_at__gt=settings.TANGGAL_TAHUN_AJARAN).filter(Q(awardee__icontains=self.query) | Q(awardee_class__icontains=self.query) | Q(name__icontains=self.query))
            elif model_name == "Extracurricular":
                queryset = Extracurricular.objects.filter(Q(name__icontains=self.query) | Q(teacher__teacher_name__icontains=self.query))
            else:
                queryset = super().get_queryset()

            if queryset and len(queryset) > 0:
                django_messages.success(self.request, f"{len(queryset)} Data Berhasil Ditemukan!")
            else:
                django_messages.error(self.request, "Data Tidak Ditemukan!")
            return queryset
        return super().get_queryset()


# KELAS DEFAULT UNTUK HALAMAN YANG MENGGUNAKAN QUERY KOMPLEKS BERTANGGAL DI LISTVIEW
class DateBasedQueryListView(ListView):
    """Base view for generic model views with shared functionality."""
    model = None
    
    def get_queryset(self) -> QuerySet[Any]:
        self.query_class = self.request.GET.get('query_class') if self.request.GET.get('query_class') else None
        self.query_day = self.request.GET.get('query_day') if self.request.GET.get('query_day') else None
        self.query_time = self.request.GET.get('query_time') if self.request.GET.get('query_time') else None
        self.query_date = self.request.GET.get('query_date')

        valid_date = parse_to_date(self.query_date)
        
        if self.query_day and self.query_class and self.query_time:
            return self.queryset.filter(schedule_day=self.query_day, schedule_class__class_name=self.query_class, schedule_time=self.query_time)
        elif self.query_time and self.query_class:
            match self.model.__qualname__:
                case "Schedule":
                    return self.queryset.filter(schedule_class__class_name=self.query_class, schedule_time=self.query_time)
                case "Report":
                    return self.queryset.filter(report_date=valid_date, schedule__schedule_class__class_name=self.query_class, schedule__schedule_time=self.query_time)
        elif self.query_class and self.query_day:
            return self.queryset.filter(schedule_day=self.query_day, schedule_class__class_name=self.query_class)
        elif self.query_day and self.query_time:
            return self.queryset.filter(schedule_day=self.query_day, schedule_time=self.query_time)
        elif self.query_day:
            return self.queryset.filter(schedule_day=self.query_day)
        elif self.query_class:
            match self.model.__qualname__:
                case "Schedule":
                    return self.queryset.filter(schedule_class__class_name=self.query_class)
                case "Report":
                    return self.queryset.filter(report_date=valid_date, schedule__schedule_class__class_name=self.query_class)
        elif self.query_time:
            match self.model.__qualname__:
                case "Schedule":
                    return self.queryset.filter(schedule_time=self.query_time)
                case "Report":
                    return self.queryset.filter(report_date=valid_date, schedule__schedule_time=self.query_time)
            
        return super().get_queryset()


# KELAS DEFAULT UNTUK HALAMAN UPLOAD EXCEL KE DATABASE
class BaseModelUploadView(BaseLoginAndPermissionRequiredView, FormView):
    """Base view for generic model views with shared functionality."""
    form_class = FileForm
    template_name = 'pages/forms.html'
    success_message: str = "Upload completed successfully!"
    error_message: str = "Upload failed!"
    model = None

    def process_excel_data(self, model_name: Model, file: str):
        """Process the uploaded Excel file and update or create Class instances."""
        if ".csv" in file.name:
            df = read_csv(file, na_filter=False)
        else:
            df = read_excel(file, na_filter=False)
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
                case "Course":
                    teacher = get_object_or_404(User, id=df.iloc[i, 5])
                    model_name.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        # course_name = df.iloc[i, 1],
                        # teacher = teacher,
                        defaults={
                            "course_name": df.iloc[i, 2],
                            "teacher": teacher,
                            "course_short_name": df.iloc[i, 2],
                            "course_code": df.iloc[i, 3],
                            "category": df.iloc[i, 4],
                        },
                    )

                case "Schedule":
                    course = get_object_or_404(Course, id=df.iloc[i, 3])
                    class_name = get_object_or_404(Class, id=df.iloc[i, 4])
                    model_name.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        schedule_day = df.iloc[i, 1],
                        schedule_time = str(df.iloc[i, 2]),
                        defaults={
                            "schedule_course": course,
                            "schedule_class": class_name,
                            "time_start": df.iloc[i, 5],
                            "time_end": df.iloc[i, 6],
                        },
                    )
                case "ReporterSchedule":
                    model_name.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        defaults={
                            "schedule_day": df.iloc[i, 1],
                            "schedule_time": df.iloc[i, 2],
                            "reporter_id": df.iloc[i, 3] or None,
                            "time_start": df.iloc[i, 4],
                            "time_end": df.iloc[i, 5],
                        },
                    )
                case "User":
                    group = get_object_or_404(Group, pk=df.iloc[i, 8])
                    obj, is_created = User.objects.update_or_create(
                        pk = df.iloc[i, 0],
                        username = df.iloc[i, 0],
                        defaults={
                            "first_name": df.iloc[i, 3],
                            "last_name": df.iloc[i, 4],
                            "email": df.iloc[i, 5],
                            "is_staff": True if df.iloc[i, 6] else False,
                            "is_superuser": True if df.iloc[i, 7] else False,
                        },
                    )
                    if is_created:
                        obj.set_password(df.iloc[i, 2])
                        obj.save()
                    obj.groups.add(group)
                case "Alumni":
                    Alumni.objects.update_or_create(
                        nis = df.iloc[i, 0],
                        defaults=dict(
                            nis = df.iloc[i, 0],
                            nisn = df.iloc[i, 1],
                            name = df.iloc[i, 2],
                            group = df.iloc[i, 3],
                            birth_place = df.iloc[i, 4],
                            birth_date = df.iloc[i, 5] or None,
                            gender = df.iloc[i, 6],
                            address = df.iloc[i, 7],
                            city = df.iloc[i, 8],
                            province = df.iloc[i, 9],
                            state = df.iloc[i, 10],
                            phone = df.iloc[i, 11],
                            last_class = df.iloc[i, 12],
                            graduate_year = df.iloc[i, 13],
                            undergraduate_department = df.iloc[i, 14],
                            undergraduate_university = df.iloc[i, 15],
                            undergraduate_university_entrance = df.iloc[i, 16],
                            postgraduate_department = df.iloc[i, 17],
                            postgraduate_university = df.iloc[i, 18],
                            postgraduate_university_entrance = df.iloc[i, 19],
                            doctoral_department = df.iloc[i, 20],
                            doctoral_university = df.iloc[i, 21],
                            doctoral_university_entrance = df.iloc[i, 22],
                            job = df.iloc[i, 23],
                            company_name = df.iloc[i, 24],
                            married = df.iloc[i, 25],
                            father_name = df.iloc[i, 26],
                            mother_name = df.iloc[i, 27],
                            family_phone = df.iloc[i, 28],
                            photo = df.iloc[i, 29],
                            )
                    )
                case _:
                    raise Http404("Nama model tidak ditemukan!")
                    
    
    def form_valid(self, form: Any) -> HttpResponse:
        try:
            if self.model is None: raise Http404("Model belum diisi pada view!")
            self.process_excel_data(self.model, form.cleaned_data["file"])
            self.object = form.save(commit=False)
            app_name, permission = self.permission_required.split(".")
            action_flag, app = permission.split("_")
            message = SendSuccessMessageLogAndWhatsapp(self.request, self.object, self.success_message, action_flag, app, app_name, message)
            message.send()
            return HttpResponseRedirect(self.get_success_url())
        except IntegrityError as e:
            self.error_message = f"Upload data sudah terbaru! Note: {str(e)}"
            django_messages.error(self.request, self.error_message)
            return super().form_invalid(form)
        except Exception as e:
            self.error_message = f"Upload data ditolak! Error: {str(e)}"
            django_messages.error(self.request, self.error_message)
            return super().form_invalid(form)



class ModelDownloadExcelView(BaseLoginAndPermissionRequiredView, ListView):
    header_names = []
    filename = ''

    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get("query")
        if query and self.kwargs.get("prestasi_active_link"):
            return self.model._default_manager.filter(Q(awardee__icontains=query) | Q(awardee_class__icontains=query) | Q(name__icontains=query))
        elif query and self.kwargs.get("prestasi_this_year_active_link"):
            return self.model._default_manager.filter(year__gte=settings.TAHUN_AWAL_AJARAN, created_at__gt=settings.TANGGAL_TAHUN_AJARAN).filter(Q(awardee__icontains=query) | Q(awardee_class__icontains=query) | Q(name__icontains=query))
        elif query and self.kwargs.get("alumni_active_link"):
            return self.model._default_manager.filter(Q(nis__icontains=query)|
                                                        Q(name__icontains=query)|
                                                        Q(nisn__icontains=query)|
                                                        Q(group__icontains=query)|
                                                        Q(graduate_year__icontains=query)|
                                                        Q(undergraduate_university__icontains=query)|
                                                        Q(undergraduate_university_entrance__icontains=query)|
                                                        Q(undergraduate_department__icontains=query))
        return super().get_queryset()

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        
        if not self.get_queryset().exists():
            raise Http404("No data can be exported to excel!")
        
        buffer = BytesIO()
        workbook = Workbook(buffer)
        merge_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        })
        title_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
            "fg_color": "yellow",
        })
        worksheet = workbook.add_worksheet()
        column_end = string.ascii_uppercase[len(self.header_names)-1]
        worksheet.merge_range(f"A1:{column_end}1", f"{self.filename}", merge_format)
        worksheet.write_row(1, 0, self.header_names, title_format)
        row = 2
        num = 1
        for data in self.get_queryset():
            if self.kwargs.get("class_active_link"):
                worksheet.write_row(row, 0, [row-1, f"{data.class_name}", f"{data.short_class_name}"])
            elif self.kwargs.get("course_active_link"):
                worksheet.write_row(row, 0, [row-1, f"{data.course_name}", f"{data.course_code}", f"{data.teacher.first_name} {data.teacher.last_name}"])
            elif self.kwargs.get("report_active_link"):
                subtitute_teacher = f"{data.subtitute_teacher.first_name}" if data.subtitute_teacher else ""
                reporter = f"{data.reporter.first_name}" if data.reporter else ""
                worksheet.write_row(row, 0, [row-1, f"{data.report_date}", f"{data.report_day}", data.status, data.schedule.schedule_time, f"{data.schedule.schedule_class}", f"{data.schedule.schedule_course.course_name}",
                                         f"{data.schedule.schedule_course.teacher.first_name}", subtitute_teacher, reporter])
            elif self.kwargs.get("schedule_active_link"):
                worksheet.write_row(row, 0, [row-1, f"{data.schedule_day}", f"{data.schedule_time}", data.schedule_class.class_name, data.schedule_course.course_name, 
                                         f"{data.schedule_course.teacher.first_name} {data.schedule_course.teacher.last_name}"])
            elif self.kwargs.get("reporter_schedule_active_link"):
                reporter = data.reporter.first_name if data.reporter else data.reporter
                worksheet.write_row(row, 0, [row-1, f"{data.schedule_day}", f"{data.schedule_time}", 
                                         f"{reporter}", f"{data.time_start}", f"{data.time_end}"])
            elif self.kwargs.get("user_active_link"):
                worksheet.write_row(row, 0, [row-1, data.username, 'Albinaa2004', data.password, data.email, f"{data.is_staff}", f"{data.is_active}",
                                         f'{data.is_superuser}', f"{data.date_joined}", f"{data.last_login}"])
            elif self.kwargs.get("program_prestasi_active_link"):
                for peserta in data.nama_peserta.all():
                    worksheet.write_row(row, 0, [num, data.program_prestasi, f"{data.tanggal}", peserta.student_name, f"{peserta.student_class}", data.pencapaian, data.catatan])
                    num += 1
                    row += 1
            elif self.kwargs.get("prestasi_active_link") or self.kwargs.get("prestasi_this_year_active_link"):
                worksheet.write_row(row, 0, [row-1, data.awardee, data.awardee_class, data.category, data.type, data.level, data.year, data.name, data.field, data.predicate, data.organizer, data.school])
            elif self.kwargs.get("alumni_active_link"):
                worksheet.write_row(row, 0, [row-1, f"{data.nis}", f"{data.nisn}", data.name, data.group, data.graduate_year, data.undergraduate_department, data.undergraduate_university, data.undergraduate_university_entrance])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{self.filename}.xlsx")



class QuickReportMixin(BaseLoginAndPermissionRequiredView, ListView):
    class_name = ['10A', '10B', '10C', '10D', '10E', '11A', '11B', '11C', '11D', '11E', '12A', '12B', '12C', '12D', '12E']
    grouped_report_data = []

    def find_and_create_reports(self, valid_date_query: Any, time: Any) -> QuerySet[Any]:
        data = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher", "reporter")\
                                    .filter(report_date=valid_date_query, schedule__schedule_time=time)\
                                    .values("id", "status", "reporter__last_name", "schedule__schedule_class", "schedule__time_start", "schedule__time_end",
                                            "schedule__schedule_course__teacher__last_name",
                                            "schedule__schedule_course__course_short_name").order_by('schedule__schedule_class')
        if len(data) == 15:
            self.grouped_report_data.append(data)
        else:
            self.create_report_objects(valid_date_query, time)
    
    def create_report_objects(self, valid_query_date: Any, schedule_time: Any) -> bool:
        # Cari data jadwal di hari sesuai query dan di waktu jam 1 sampai  9
        schedule_list = Schedule.objects.select_related("schedule_course", "schedule_course__teacher","schedule_class") \
                                .filter(schedule_day=get_day(valid_query_date), schedule_time=schedule_time)
        try:
            reporter_schedule = ReporterSchedule.objects.select_related("reporter").get(schedule_day=get_day(valid_query_date), schedule_time=schedule_time)
        except:
            reporter_schedule = None
        # Jika tidak ditemukan, maka nilai False
        if len(schedule_list) == 15:
            # Jika ditemukan, maka buat laporan dengan jadwal dimasukkan satu per satu
            for schedule in schedule_list:
                obj, is_created = Report.objects.update_or_create(
                    report_date = valid_query_date,
                    schedule = schedule,
                    # reporter = reporter_schedule.reporter,
                    defaults={
                        'reporter': reporter_schedule.reporter
                    }
                )
            return True
        return False

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        query_date = self.request.GET.get('query_date', datetime.now().date())
        valid_date = parse_to_date(query_date)
        day = get_day(valid_date)
        self.grouped_report_data = []
        if day == "Ahad":
            for i in range(1, 8):
                self.find_and_create_reports(valid_date, i)

                
        elif day != "Jumat":
            for i in range(1, 10):
                self.find_and_create_reports(valid_date, i)

        
        context = super().get_context_data(**kwargs)
        context["grouped_report_data"] = self.grouped_report_data
        context["class"] = self.class_name
        query_date = self.request.GET.get('query_date', str(datetime.now().date()))
        context["query_date"] = query_date
        return context
    

class ReportUpdateReporterMixin(BaseLoginAndPermissionFormView, FormView):
    model = Report
    active_link = 'report'
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
    

class ReportUpdateQuickViewMixin(BaseLoginAndPermissionFormView, UpdateView):
    model = Report
    active_link = 'report'
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
            reporter = object.reporter.first_name

        message = f"laporan piket {object.report_day} {object.report_date} Jam ke-{object.schedule.schedule_time} {object.schedule.schedule_course} dengan status {status}"
        redirect_url = reverse(self.redirect_url)
        query_params = f'?query_date={object.report_date}'
        self.object = form.save()
        app_name, permission = self.permission_required.split(".")
        action_flag, app = permission.split("_")
        message = SendSuccessMessageLogAndWhatsapp(self.request, self.object, self.success_message, action_flag, app, app_name, message)
        message.send()
        return redirect(redirect_url + query_params)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["object"] = self.get_object()
        return context



class GeneralContextMixin(View):
    form_name = ''

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = self.form_name
        c["query"] = self.request.GET.get("query")
        c["month"] = self.request.GET.get("month")
        c["year"] = self.request.GET.get("year")
        return c


class GeneralAuthPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin, GeneralContextMixin):
    raise_exception = True


class GeneralFormValidateMixin(GeneralAuthPermissionMixin, FormView):
    success_message: str = "Input data berhasil!"
    error_message: str = "Gagal input data. Ada sesuatu yang salah!"
    app_name = ''
    type_url = ''
    slug_url = ''

    def form_valid(self, form: Any) -> HttpResponse:
        self.object = form.save()
        django_messages.success(self.request, self.success_message)
        UserLog.objects.create(
            user = self.request.user.teacher,
            action_flag = self.form_name.upper(),
            app = self.app_name.upper(),
            message = f"berhasil {self.form_name.lower()} data {self.app_name} dengan detail berikut: {self.object}"
        )
        send_WA_create_update_delete(self.request.user.teacher.no_hp, self.form_name.lower(), f'data {self.app_name} dengan detail berikut: {self.object}', self.type_url, self.slug_url)
        return super().form_valid(form)
    
    def form_invalid(self, form: Any) -> HttpResponse:
        django_messages.success(self.request, self.error_message)
        return super().form_invalid(form)
    

class GeneralFormDeleteMixin(GeneralAuthPermissionMixin, DeleteView):
    app_name = ''
    type_url = ''
    slug_url = ''

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.obj = self.get_object()
        UserLog.objects.create(
            user = self.request.user.teacher,
            action_flag = 'DELETE',
            app = self.app_name.upper(),
            message = f"berhasil menghapus data {self.app_name} dengan detail berikut: {self.obj}"
        )
        send_WA_create_update_delete(request.user.teacher.no_hp, 'menghapus', f'data {self.app_name} dengan detail berikut: {self.obj}', self.type_url, self.slug_url)
        django_messages.success(self.request, "Data Berhasil Dihapus! :)")
        return super().post(request, *args, **kwargs)
    


class GeneralDownloadExcelView(GeneralAuthPermissionMixin):
    header_names = []
    filename = ''
    queryset = None
    app_name = ''

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        query = self.request.GET.get("query")
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, self.header_names)
        row = 1
        if query:
            for data in self.queryset.filter(Q(nis__icontains=query or "")|
                                         Q(name__icontains=query)|
                                         Q(nisn__icontains=query or "")|
                                         Q(group__icontains=query)|
                                         Q(graduate_year__icontains=query)|
                                         Q(undergraduate_university__icontains=query)|
                                         Q(undergraduate_university_entrance__icontains=query)|
                                         Q(undergraduate_department__icontains=query)):
                if self.app_name == 'Alumni':
                    worksheet.write_row(row, 0, [row, f"{data.nis}", f"{data.nisn}", data.name, data.group, data.graduate_year, data.undergraduate_department, data.undergraduate_university, data.undergraduate_university_entrance])
                row += 1
        else:
            for data in self.queryset:
                if self.app_name == 'Alumni':
                    worksheet.write_row(row, 0, [row, f"{data.nis}", f"{data.nisn}", data.name, data.group, data.graduate_year, data.undergraduate_department, data.undergraduate_university, data.undergraduate_university_entrance])
                row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)


        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DOWNLOAD",
            app=self.app_name.upper(),
            message=f"berhasil download daftar {self.app_name.lower()} dalam format Excel"
        )
        send_WA_general(request.user.teacher.no_hp, 'download', f'file Excel data {self.app_name.lower()}')
        return FileResponse(buffer, as_attachment=True, filename=self.filename)



class ListViewWithGridAndSearch(TitleView, LinkView, SearchView, BaseQueryListView):
    pass
    
class ListViewWithGridAndDateBasedSearch(TitleView, LinkView, SearchView, DateBasedQueryListView):
    pass

class ListViewWithTableAndSearch(TitleView, LinkView, SearchView, TableView, BaseQueryListView):
    pass

class ListViewWithTableAndDateBasedSearch(TitleView, LinkView, SearchView, TableView, DateBasedQueryListView):
    pass