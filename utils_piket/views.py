import calendar
from collections import defaultdict
from io import BytesIO
import json
from typing import Any
from django.db.models.query import QuerySet
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from classes.models import Class
from courses.models import Course
from django.contrib.auth.models import User
from django.db.models import Count, Q
from datetime import datetime
from schedules.models import ReporterSchedule, Schedule
from reports.models import Report
from userlog.models import UserLog
from utils_piket.mixins import BaseAuthorizedModelView, BaseModelQueryListView
from utils_piket.constants import WEEKDAYS
from xlsxwriter import Workbook

from utils_piket.whatsapp_albinaa import send_whatsapp_device_status, send_whatsapp_message



class DashboardListView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    queryset = Report.objects.all()
    template_name = 'dashboard.html'
    menu_name = "report"
    permission_required = 'reports.view_report'
    raise_exception = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Collect and organize data for dashboard context.
        """
        data = super().get_context_data(**kwargs)
        today = datetime.now()
        today_str = str(today.date())
        today_weekday = WEEKDAYS.get(today.weekday())

        # Users
        active_users = User.objects.filter(is_active=True)
        data["sum_of_user"] = active_users
        data["sum_of_user_category"] = active_users.values('is_superuser').annotate(dcount=Count('is_superuser'))

        # Classes
        all_classes = Class.objects.all()
        data["sum_of_class"] = all_classes
        data["sum_of_class_category"] = all_classes.values('category').annotate(dcount=Count('category'))

        # Courses
        courses = Course.objects.exclude(course_code__in=["APE", "LQ1", "TKL"]).select_related("teacher")
        distinct_courses = courses.values("course_name", "category").distinct()
        data["sum_of_course"] = distinct_courses
        data["sum_of_course_syari"] = distinct_courses.filter(category="Syar'i")
        data["sum_of_course_ashri"] = distinct_courses.filter(category="Ashri")

        # Schedules
        all_schedules = Schedule.objects.select_related("schedule_course", "schedule_course__teacher","schedule_class").all()
        today_schedules = all_schedules.filter(schedule_day=today_weekday)
        data["sum_of_schedule"] = all_schedules
        data["sum_of_schedule_today"] = today_schedules
        data["sum_of_schedule_teacher"] = today_schedules.values('schedule_course__teacher').distinct().count()
        data["sum_of_schedule_teacher_syari"] = today_schedules.filter(schedule_course__category="Syar'i").values('schedule_course__course_name').distinct().count()
        data["sum_of_schedule_teacher_ashri"] = today_schedules.filter(schedule_course__category="Ashri").values('schedule_course__course_name').distinct().count()

        # Reports
        today_reports = self.queryset.filter(report_date=today_str)
        data["sum_of_report_today"] = today_reports
        data["sum_of_report_status"] = self.queryset.values('status').annotate(dcount=Count('status'))
        data["sum_of_report_today_status"] = today_reports.values('status').annotate(dcount=Count('status'))
        data["report_latest"] = self.queryset[:10]

        # Userlogs

        data["userlogs"] = UserLog.objects.all()[:8]
        return data

    
class TeacherRecapListView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = "report"
    permission_required = 'reports.view_report'
    template_name = 'teacher-reporter-recap.html'
    raise_exception = False

    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')

        if date_start and date_end:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
                                .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                                .filter(report_date__gte=date_start, report_date__lte=date_end)\
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
                                .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                                .filter(report_date__month=datetime.now().month, report_date__year=datetime.now().year)\
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
    

class TeacherAbsenceListView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = "report"
    permission_required = 'reports.view_report'
    template_name = 'teacher-reporter-detail.html'
    raise_exception = False

    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        if date_start and date_end:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher", "schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__gte=date_start, report_date__lte=date_end, status__in=["Izin", "Sakit", "Tanpa Keterangan"])\
                             .values('report_date','schedule__schedule_course__teacher__teacher_name', "schedule__schedule_class__short_class_name", "schedule__schedule_time", "status")\
                             .distinct().order_by("-report_date", "schedule__schedule_class__short_class_name", "schedule__schedule_time")
        
        else:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher", "schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__month=datetime.now().month, report_date__year=datetime.now().year, status__in=["Izin", "Sakit", "Tanpa Keterangan"])\
                             .values('report_date','schedule__schedule_course__teacher__teacher_name', "schedule__schedule_class__short_class_name", "schedule__schedule_time", "status")\
                             .distinct().order_by("-report_date", "schedule__schedule_class__short_class_name", "schedule__schedule_time")

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
    

class TeacherRecapDetailView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = "report"
    permission_required = 'reports.view_report'
    raise_exception = False
    template_name = 'teacher-reporter-detail.html'

    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        teacher_id = self.kwargs.get("teacher_id")
        if date_start and date_end:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher", "schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__gte=date_start, report_date__lte=date_end, schedule__schedule_course__teacher_id=teacher_id, status__in=["Izin", "Sakit", "Tanpa Keterangan"])\
                             .values('report_date','schedule__schedule_course__teacher__teacher_name', "schedule__schedule_class__short_class_name", "schedule__schedule_time", "status")\
                             .distinct().order_by("-report_date", "schedule__schedule_class__short_class_name", "schedule__schedule_time")
        
        else:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher", "schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__month=datetime.now().month, report_date__year=datetime.now().year, schedule__schedule_course__teacher_id=teacher_id, status__in=["Izin", "Sakit", "Tanpa Keterangan"])\
                             .values('report_date','schedule__schedule_course__teacher__teacher_name', "schedule__schedule_class__short_class_name", "schedule__schedule_time", "status")\
                             .distinct().order_by("-report_date", "schedule__schedule_class__short_class_name", "schedule__schedule_time")

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


class TeacherRecapDownloadExcelView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = 'report'
    permission_required = 'reports.view_report'
    template_name='teacher-reporter-recap.html'
    
    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        if date_start and date_end:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__gte=date_start, report_date__lte=date_end)\
                             .values('schedule__schedule_course__teacher__teacher_name')\
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
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__month=datetime.now().month, report_date__year=datetime.now().year)\
                             .values('schedule__schedule_course__teacher__teacher_name')\
                             .annotate(
                                 hadir_count=Count('status',  filter=Q(status="Hadir")),
                                 izin_count=Count('status',  filter=Q(status="Izin")),
                                 sakit_count=Count('status',  filter=Q(status="Sakit")),
                                 alpha_count=Count('status',  filter=Q(status="Tanpa Keterangan")),
                                 all_count=Count('status'),
                                 )\
                             .distinct().order_by()
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, ['No', 'GURU', 'HADIR', 'IZIN', 'SAKIT', 'ALPHA', 'PERSENTASE'])
        row = 1
        
        for data in self.get_queryset():
            percentage = "{:.2f}".format(data.get("hadir_count")/data.get("all_count")*100)
            worksheet.write_row(row, 0, [row, data.get("schedule__schedule_course__teacher__teacher_name"), data.get("hadir_count"), data.get("izin_count"), data.get("sakit_count"), data.get("alpha_count"), f"{percentage}%"])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f'REKAP KEHADIRAN GURU SMA IT Al Binaa.xlsx')
    

class TeacherAbsenceDownloadExcelView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = 'report'
    permission_required = 'reports.view_report'
    template_name='teacher-reporter-recap.html'
    
    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        if date_start and date_end:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher", "schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__gte=date_start, report_date__lte=date_end, status__in=["Izin", "Sakit", "Tanpa Keterangan"])\
                             .values('report_date','schedule__schedule_course__teacher__teacher_name', "schedule__schedule_class__short_class_name", "schedule__schedule_time", "status")\
                             .distinct().order_by("-report_date", "schedule__schedule_class__short_class_name", "schedule__schedule_time")

        else: 
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher", "schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__month=datetime.now().month, report_date__year=datetime.now().year, status__in=["Izin", "Sakit", "Tanpa Keterangan"])\
                             .values('report_date','schedule__schedule_course__teacher__teacher_name', "schedule__schedule_class__short_class_name", "schedule__schedule_time", "status")\
                             .distinct().order_by("-report_date", "schedule__schedule_class__short_class_name", "schedule__schedule_time")
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, ['No', 'TANGGAL', 'GURU', 'KELAS', 'JAM KE', 'STATUS', 'KETERANGAN'])
        row = 1
        
        for data in self.get_queryset():
            worksheet.write_row(row, 0, [row, str(data.get("report_date")), data.get("schedule__schedule_course__teacher__teacher_name"), data.get("schedule__schedule_class__short_class_name"), data.get("schedule__schedule_time"), data.get("status")])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f'REKAP KETIDAKHADIRAN GURU SMA IT Al Binaa.xlsx')
    

class TeacherAbsenceDetailDownloadExcelView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = 'report'
    permission_required = 'reports.view_report'
    template_name='teacher-reporter-recap.html'
    
    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        teacher_id = self.kwargs.get("teacher_id")

        if date_start and date_end:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher", "schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__month=date_start, report_date__year=date_end, schedule__schedule_course__teacher_id=teacher_id, status__in=["Izin", "Sakit", "Tanpa Keterangan"])\
                             .values('report_date','schedule__schedule_course__teacher__teacher_name', "schedule__schedule_class__short_class_name", "schedule__schedule_time", "status")\
                             .distinct().order_by("-report_date", "schedule__schedule_class__short_class_name", "schedule__schedule_time")
        
        else:
            return super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher", "schedule__schedule_class", "subtitute_teacher")\
                             .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
                             .filter(report_date__month=datetime.now().month, report_date__year=datetime.now().year, schedule__schedule_course__teacher_id=teacher_id, status__in=["Izin", "Sakit", "Tanpa Keterangan"])\
                             .values('report_date','schedule__schedule_course__teacher__teacher_name', "schedule__schedule_class__short_class_name", "schedule__schedule_time", "status")\
                             .distinct().order_by("-report_date", "schedule__schedule_class__short_class_name", "schedule__schedule_time")
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, ['No', 'TANGGAL', 'GURU', 'KELAS', 'JAM KE', 'STATUS', 'KETERANGAN'])
        row = 1
        
        for data in self.get_queryset():
            worksheet.write_row(row, 0, [row, str(data.get("report_date")), data.get("schedule__schedule_course__teacher__teacher_name"), data.get("schedule__schedule_class__short_class_name"), data.get("schedule__schedule_time"), data.get("status")])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f'DETAIL KETIDAKHADIRAN GURU SMA IT Al Binaa.xlsx')
    


# class ReporterRecapListView(BaseAuthorizedModelView, BaseModelQueryListView):
#     model = Report
#     menu_name = "report"
#     permission_required = 'reports.view_report'
#     raise_exception = False
#     template_name = 'teacher-reporter-recap.html'

#     def get_queryset(self) -> QuerySet[Any]:
#         date_start = self.request.GET.get('date_start')
#         date_end = self.request.GET.get('date_end')
#         this_year = datetime.now().year
#         this_month = datetime.now().month

#         if date_start and date_end:
#             # Create a calendar object for the month
#             this_month = datetime.strptime(date_start, "%Y-%m-%d").month
#             this_year = datetime.strptime(date_start, "%Y-%m-%d").year
#             month_calendar = calendar.monthcalendar(this_year, this_month)
#         else:
#             month_calendar = calendar.monthcalendar(datetime.now().year, datetime.now().month)

        
#         # Count the number of Tuesdays in the month
#         # day_count_in_month = {'Senin': 4, 'Selasa': 4, 'Rabu': 5, 'Kamis': 5, 'Jumat': 5, 'Sabtu': 4, 'Ahad': 4}
#         day_count_in_month = {}
#         for k, v in WEEKDAYS.items():
#             day_count_in_month[v] = sum(1 for week in month_calendar if week[k] != 0)
        
#         reporters_counts_data = []
#         # {'Tri Setyo Mardi Utomo, S.Pd': 26, 'Suharyadi, M. Pd., Gr.': 8, 'Alif Rezky, M.Pd.': 16, 'Muh. Halidi, S.Si.': 8, 'Radivan Tiravi': 27, 'Wawanto, S. Si.': 8, 'Dadan Ridwanuloh, M.Si.': 8, 'Arie Afriansyah, Lc.': 18, 'Agus Setiawan, S.T.': 8, 'Syafiq Muhammad Rwenky, B.A.': 10, 'Ahmad Reza Febrianto': 18, 'Aam Hamdani, S.Pd.': 20, 'Rifqi Aqwamuddin, Lc.': 10, 'Hario Sadewo P, S.Pd.': 8, 'Harlan, S. Pd.': 8, 'Firyan Ramdhani, S.Pd.': 8, 'Mohamad Alam Novian, M. Pd.': 8}

#         for day_key, value_day_count in day_count_in_month.items():
#             data = ReporterSchedule.objects.filter(schedule_day=day_key).exclude(reporter__isnull=True)\
#                                             .values("schedule_day", "reporter__teacher_name")\
#                                             .annotate(rcount=Count("reporter__teacher_name")*value_day_count)\
#                                             .distinct().order_by("reporter__teacher_name")
#             # print(data)
#             for obj in data:
#                 reporters_counts_data.append(obj)
        
#         # Sort list_of_dict by reporter__teacher_name
#         sorted_reporters_counts_data = sorted(reporters_counts_data, key=lambda x: x['reporter__teacher_name'])

#         # Dictionary to store aggregated counts
#         aggregated_counts = defaultdict(int)

#         # Sum the rcount for each reporter__teacher_name
#         for item in sorted_reporters_counts_data:
#             aggregated_counts[item['reporter__teacher_name']] += item['rcount']
        
        
        
#         # Convert back to a list of dicts if needed
#         result = [{'reporter__teacher_name': name, 'total_rcount': count} for name, count in aggregated_counts.items()]

#         print(len(result))

#         if date_start and date_end:
#             null_reporter = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
#                                       .filter(report_date__gte=date_start, report_date__lte=date_end, reporter__isnull=True)\
#                                       .exclude(schedule__in=[241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525])\
#                                       .values("report_date", "schedule__schedule_day", "schedule__schedule_time")\
#                                       .distinct().order_by()
#         else:
#             null_reporter = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
#                                       .filter(report_date__month=this_month, report_date__year=this_year, reporter__isnull=True)\
#                                       .exclude(schedule__in=[241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525])\
#                                       .values("report_date", "schedule__schedule_day", "schedule__schedule_time")\
#                                       .distinct().order_by()
#         # <QuerySet [{'report_date': datetime.date(2025, 1, 21), 'schedule__schedule_day': 'Selasa', 'schedule__schedule_time': '1'}]>

#         absen_group_data = []

#         for obj in null_reporter:
#             data = ReporterSchedule.objects.filter(schedule_day=obj.get("schedule__schedule_day"), schedule_time=obj.get("schedule__schedule_time"))\
#                                             .values("reporter__teacher_name").annotate(absen_count=Count("reporter__teacher_name")).order_by()
#             for obj in data:
#                 absen_group_data.append(obj)
#             # <QuerySet [<ReporterSchedule: Selasa | Jam ke-1 | radivan_tiravi>]>
#         if date_start and date_end:
#             data = super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
#                              .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
#                              .filter(report_date__gte=date_start, report_date__lte=date_end, reporter__isnull=False)\
#                              .values('reporter__teacher_name')\
#                              .annotate(hadir_count=Count('reporter__teacher_name')/15)\
#                              .order_by('reporter__teacher_name')
#         else:
#             data = super().get_queryset().select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
#                              .exclude(schedule__schedule_course__course_code__in=["APE", "TKL"])\
#                              .filter(report_date__month=this_month, report_date__year=this_year, reporter__isnull=False)\
#                              .values('reporter__teacher_name')\
#                              .annotate(hadir_count=Count('reporter__teacher_name')/15)\
#                              .order_by('reporter__teacher_name')
        
#         print(len(data))
#         for i in data:
#             print(i)
#         for index in range(len(data)):
#             data[index].update(result[index])
#             for i in range(len(absen_group_data)):
#                 if len(absen_group_data) > 0 and data[index].get("reporter__teacher_name") == absen_group_data[i].get("reporter__teacher_name"):
#                     data[index].update(absen_group_data[i])
        
#         return data
    
class ReporterRecapListView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = "report"
    permission_required = 'reports.view_report'
    raise_exception = False
    template_name = 'teacher-reporter-recap.html'

    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        this_year = datetime.now().year
        this_month = datetime.now().month

        if date_start and date_end:
            # Create a calendar object for the month
            this_month = datetime.strptime(date_start, "%Y-%m-%d").month
            this_year = datetime.strptime(date_start, "%Y-%m-%d").year
            month_calendar = calendar.monthcalendar(this_year, this_month)
        else:
            month_calendar = calendar.monthcalendar(datetime.now().year, datetime.now().month)

        
        # Count the number of Tuesdays in the month
        # day_count_in_month = {'Senin': 4, 'Selasa': 4, 'Rabu': 5, 'Kamis': 5, 'Jumat': 5, 'Sabtu': 4, 'Ahad': 4}
        day_count_in_month = {}
        for k, v in WEEKDAYS.items():
            day_count_in_month[v] = sum(1 for week in month_calendar if week[k] != 0)
        
        reporters_counts_data = []
        # {'Tri Setyo Mardi Utomo, S.Pd': 26, 'Suharyadi, M. Pd., Gr.': 8, 'Alif Rezky, M.Pd.': 16, 'Muh. Halidi, S.Si.': 8, 'Radivan Tiravi': 27, 'Wawanto, S. Si.': 8, 'Dadan Ridwanuloh, M.Si.': 8, 'Arie Afriansyah, Lc.': 18, 'Agus Setiawan, S.T.': 8, 'Syafiq Muhammad Rwenky, B.A.': 10, 'Ahmad Reza Febrianto': 18, 'Aam Hamdani, S.Pd.': 20, 'Rifqi Aqwamuddin, Lc.': 10, 'Hario Sadewo P, S.Pd.': 8, 'Harlan, S. Pd.': 8, 'Firyan Ramdhani, S.Pd.': 8, 'Mohamad Alam Novian, M. Pd.': 8}

        for day_key, value_day_count in day_count_in_month.items():
            data = ReporterSchedule.objects.filter(schedule_day=day_key).exclude(reporter__isnull=True)\
                                            .values("reporter__teacher_name")\
                                            .annotate(expected_count=Count("reporter__teacher_name")*value_day_count)\
                                            .distinct().order_by("reporter__teacher_name")
            # print(data)
            for obj in data:
                reporters_counts_data.append(obj)
        
        # Sort list_of_dict by reporter__teacher_name
        sorted_reporters_counts_data = sorted(reporters_counts_data, key=lambda x: x['reporter__teacher_name'])

        # Dictionary to store aggregated counts
        aggregated_counts = defaultdict(int)

        # Sum the rcount for each reporter__teacher_name
        for item in sorted_reporters_counts_data:
            aggregated_counts[item['reporter__teacher_name']] += item['expected_count']

        # Convert back to a list of dicts if needed
        result = [{'reporter__teacher_name': name, 'expected_count': count} for name, count in aggregated_counts.items()]
                
        if date_start and date_end:
            reports_data = list(Report.objects.filter(report_date__gte=date_start, report_date__lte=date_end)\
                                    .exclude(reporter__isnull=True).values("reporter__teacher_name")\
                                    .annotate(real_count=Count("reporter__teacher_name")/15)\
                                    .order_by("reporter__teacher_name"))
        
            null_reporter = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
                                      .filter(report_date__gte=date_start, report_date__lte=date_end, reporter__isnull=True)\
                                      .exclude(schedule__in=[241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525])\
                                      .values("report_date", "schedule__schedule_day", "schedule__schedule_time")\
                                      .distinct().order_by()
        else:
            reports_data = list(Report.objects.filter(report_date__month=this_month, report_date__year=this_year)\
                                    .exclude(reporter__isnull=True).values("reporter__teacher_name")\
                                    .annotate(real_count=Count("reporter__teacher_name")/15)\
                                    .order_by("reporter__teacher_name"))
            
            null_reporter = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
                                      .filter(report_date__month=this_month, report_date__year=this_year, reporter__isnull=True)\
                                      .exclude(schedule__in=[241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525])\
                                      .values("schedule__schedule_day", "schedule__schedule_time")\
                                      .distinct().order_by()
        
        absen_group_data = []

        for obj in null_reporter:
            data = ReporterSchedule.objects.filter(schedule_day=obj.get("schedule__schedule_day"), schedule_time=obj.get("schedule__schedule_time"))\
                                            .values("reporter__teacher_name").annotate(absen_count=Count("reporter__teacher_name")).order_by()
            for obj in data:
                absen_group_data.append(obj)
        
        lookup = {d['reporter__teacher_name']: d for d in reports_data}
    
        # Merge data from dict_one into dict_two
        for entry in result:
            key = entry['reporter__teacher_name']
            if key in lookup:
                # Update existing entry in dict_two
                lookup[key].update(entry)
            else:
                # Append new entry from dict_one to dict_two
                reports_data.append(entry)

        # Merge data from dict_one into dict_two
        for entry in absen_group_data:
            key = entry['reporter__teacher_name']
            if key in lookup:
                # Update existing entry in dict_two
                lookup[key].update(entry)
            else:
                # Append new entry from dict_one to dict_two
                reports_data.append(entry)
        
        return reports_data
    

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
        context["reporters"] = True
        return context
    


class ReporterRecapDownloadExcelView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = 'report'
    permission_required = 'reports.view_report'
    template_name='teacher-reporter-recap.html'
    
    def get_queryset(self) -> QuerySet[Any]:
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        this_year = datetime.now().year
        this_month = datetime.now().month

        if date_start and date_end:
            # Create a calendar object for the month
            this_month = datetime.strptime(date_start, "%Y-%m-%d").month
            this_year = datetime.strptime(date_start, "%Y-%m-%d").year
            month_calendar = calendar.monthcalendar(this_year, this_month)
        else:
            month_calendar = calendar.monthcalendar(datetime.now().year, datetime.now().month)

        
        # Count the number of Tuesdays in the month
        # day_count_in_month = {'Senin': 4, 'Selasa': 4, 'Rabu': 5, 'Kamis': 5, 'Jumat': 5, 'Sabtu': 4, 'Ahad': 4}
        day_count_in_month = {}
        for k, v in WEEKDAYS.items():
            day_count_in_month[v] = sum(1 for week in month_calendar if week[k] != 0)
        
        reporters_counts_data = []
        # {'Tri Setyo Mardi Utomo, S.Pd': 26, 'Suharyadi, M. Pd., Gr.': 8, 'Alif Rezky, M.Pd.': 16, 'Muh. Halidi, S.Si.': 8, 'Radivan Tiravi': 27, 'Wawanto, S. Si.': 8, 'Dadan Ridwanuloh, M.Si.': 8, 'Arie Afriansyah, Lc.': 18, 'Agus Setiawan, S.T.': 8, 'Syafiq Muhammad Rwenky, B.A.': 10, 'Ahmad Reza Febrianto': 18, 'Aam Hamdani, S.Pd.': 20, 'Rifqi Aqwamuddin, Lc.': 10, 'Hario Sadewo P, S.Pd.': 8, 'Harlan, S. Pd.': 8, 'Firyan Ramdhani, S.Pd.': 8, 'Mohamad Alam Novian, M. Pd.': 8}

        for day_key, value_day_count in day_count_in_month.items():
            data = ReporterSchedule.objects.filter(schedule_day=day_key).exclude(reporter__isnull=True)\
                                            .values("reporter__teacher_name")\
                                            .annotate(expected_count=Count("reporter__teacher_name")*value_day_count)\
                                            .distinct().order_by("reporter__teacher_name")
            # print(data)
            for obj in data:
                reporters_counts_data.append(obj)
        
        # Sort list_of_dict by reporter__teacher_name
        sorted_reporters_counts_data = sorted(reporters_counts_data, key=lambda x: x['reporter__teacher_name'])

        # Dictionary to store aggregated counts
        aggregated_counts = defaultdict(int)

        # Sum the rcount for each reporter__teacher_name
        for item in sorted_reporters_counts_data:
            aggregated_counts[item['reporter__teacher_name']] += item['expected_count']

        # Convert back to a list of dicts if needed
        result = [{'reporter__teacher_name': name, 'expected_count': count} for name, count in aggregated_counts.items()]
                
        if date_start and date_end:
            reports_data = list(Report.objects.filter(report_date__gte=date_start, report_date__lte=date_end)\
                                    .exclude(reporter__isnull=True).values("reporter__teacher_name")\
                                    .annotate(real_count=Count("reporter__teacher_name")/15)\
                                    .order_by("reporter__teacher_name"))
        
            null_reporter = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
                                      .filter(report_date__gte=date_start, report_date__lte=date_end, reporter__isnull=True)\
                                      .exclude(schedule__in=[241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525])\
                                      .values("report_date", "schedule__schedule_day", "schedule__schedule_time")\
                                      .distinct().order_by()
        else:
            reports_data = list(Report.objects.filter(report_date__month=this_month, report_date__year=this_year)\
                                    .exclude(reporter__isnull=True).values("reporter__teacher_name")\
                                    .annotate(real_count=Count("reporter__teacher_name")/15)\
                                    .order_by("reporter__teacher_name"))
            
            null_reporter = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher")\
                                      .filter(report_date__month=this_month, report_date__year=this_year, reporter__isnull=True)\
                                      .exclude(schedule__in=[241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525])\
                                      .values("schedule__schedule_day", "schedule__schedule_time")\
                                      .distinct().order_by()
        
        absen_group_data = []

        for obj in null_reporter:
            data = ReporterSchedule.objects.filter(schedule_day=obj.get("schedule__schedule_day"), schedule_time=obj.get("schedule__schedule_time"))\
                                            .values("reporter__teacher_name").annotate(absen_count=Count("reporter__teacher_name")).order_by()
            for obj in data:
                absen_group_data.append(obj)
        
        lookup = {d['reporter__teacher_name']: d for d in reports_data}
    
        # Merge data from dict_one into dict_two
        for entry in result:
            key = entry['reporter__teacher_name']
            if key in lookup:
                # Update existing entry in dict_two
                lookup[key].update(entry)
            else:
                # Append new entry from dict_one to dict_two
                reports_data.append(entry)

        # Merge data from dict_one into dict_two
        for entry in absen_group_data:
            key = entry['reporter__teacher_name']
            if key in lookup:
                # Update existing entry in dict_two
                lookup[key].update(entry)
            else:
                # Append new entry from dict_one to dict_two
                reports_data.append(entry)
        
        return reports_data
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, ['No', 'PETUGAS PIKET', 'JAM HADIR', 'JAM TIDAK HADIR', 'JUMLAH JAM', 'PERSENTASE'])
        row = 1
        
        for data in self.get_queryset():
            percentage = "{:.2f}".format(data.get("real_count", 0)/data.get("expected_count", data.get("real_count", 0))*100)
            worksheet.write_row(row, 0, [row, data.get("reporter__teacher_name"), data.get("real_count"), data.get("absen_count"), data.get("expected_count", data.get("real_count", 0)), f"{percentage}%"])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f'REKAP KEHADIRAN TIM PIKET SMA IT Al Binaa.xlsx')
    


@csrf_exempt  # Disable CSRF for this endpoint
def device_webhook(request):    
    if request.method == "POST":
        try:
            # Parse the incoming JSON payload
            payload = json.loads(request.body)

            send_whatsapp_device_status(id_device=payload.get('deviceId'), status=payload.get('status'), note=payload.get('note'), time=payload.get('timestamp'))
            
            # Send a response back to acknowledge the webhook
            return JsonResponse({"message": "Webhook received successfully"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return HttpResponse("Hello, World!")

@csrf_exempt  # Disable CSRF for this endpoint
def tracking_webhook(request):    
    if request.method == "POST":
        try:
            # Parse the incoming JSON payload
            payload = json.loads(request.body)

            message = f"Phone {payload.get('phone')} status: {payload.get('status')} note: {payload.get('note')} sender: {payload.get('sender')}"

            # send_whatsapp_action(user=payload.get('id'), messages=message)
            
            # Send a response back to acknowledge the webhook
            return JsonResponse({"message": "Webhook received successfully"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return HttpResponse("Hello, World!")
    


@csrf_exempt  # Disable CSRF for this endpoint
def message_webhook(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON payload
            payload = json.loads(request.body)
            
            # Check if the message is a group or personal message
            if payload.get("isGroup"):
                # Process group message
                send_whatsapp_message(pushName=payload.get("pushName"), groupSubject=payload["group"].get("subject"), groupSender=payload["group"].get("sender"), message=payload.get("message"), timestamp=payload.get("timestamp"), file=payload.get("file"), url=payload.get("url"))
            else:
                # Process personal message
                send_whatsapp_message(pushName=payload.get("pushName"), sender=payload.get("sender"), message=payload.get("message"), timestamp=payload.get("timestamp"), file=payload.get("file"), url=payload.get("url"))
            # Send a response back to acknowledge the webhook
            return JsonResponse({"message": "Webhook processed successfully"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)