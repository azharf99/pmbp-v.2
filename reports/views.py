import calendar
from collections import defaultdict
from datetime import date, datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages as msg
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DetailView, FormView
from reports.forms import ReportFormV2, SubmitForm
from classes.models import Class
from reports.models import Report
from typing import Any
from django.urls import reverse, reverse_lazy
from schedules.models import ReporterSchedule
from users.models import Teacher
from utils_piket.mixins import BaseAuthorizedFormView, BaseModelDateBasedListView, BaseModelDeleteView, BaseModelUploadView, BaseAuthorizedModelView, ModelDownloadExcelView, BaseModelQueryListView, QuickReportMixin, ReportUpdateQuickViewMixin, ReportUpdateReporterMixin, SubmitViewMixins
from utils_piket.validate_datetime import get_day
from utils_piket.whatsapp_albinaa import send_whatsapp_group, send_whatsapp_report
# Create your views here.
    
class ReportListView(BaseAuthorizedModelView, BaseModelDateBasedListView):
    model = Report
    queryset = Report.objects.select_related("schedule__schedule_course__course", "schedule__schedule_course__teacher", "schedule__schedule_time", "schedule__schedule_class", "schedule__teacher", "subtitute_teacher", "reporter").all()
    menu_name = 'report'
    permission_required = 'reports.view_report'
    raise_exception = False
    paginate_by = 105

class ReportDetailView(BaseAuthorizedModelView, DetailView):
    model = Report
    menu_name = 'report'
    permission_required = 'reports.view_report'


class ReportQuickCreateViewV3(QuickReportMixin):
    model = Report
    menu_name = 'report'
    form_class = ReportFormV2
    template_name = 'reports/report_quick_form-v3.html'
    permission_required = 'reports.add_report'
    class_name = [name.short_class_name for name in Class.objects.filter(category="Putra")]
    queryset = Report.objects.select_related("schedule__schedule_course__course", "schedule__schedule_course__teacher", "schedule__schedule_time", "schedule__schedule_class", "schedule__teacher", "subtitute_teacher", "reporter")


class ReportPutriQuickCreateViewV3(QuickReportMixin):
    model = Report
    menu_name = 'report'
    form_class = ReportFormV2
    template_name = 'reports/report_quick_form-v3.html'
    permission_required = 'reports.add_report'
    type = "putri"
    class_name = [name.short_class_name for name in Class.objects.filter(category="Putri")]
    queryset = Report.objects.select_related("schedule__schedule_course__course", "schedule__schedule_course__teacher", "schedule__schedule_time", "schedule__schedule_class", "schedule__teacher", "subtitute_teacher", "reporter")



class SubmitButtonView(SubmitViewMixins):
    form_class = SubmitForm
    template_name = 'reports/report_quick_form-v3.html'
    success_url = reverse_lazy("report-quick-create-v3")
    queryset = Report.objects.select_related("schedule__schedule_course__course", "schedule__schedule_course__teacher", "schedule__schedule_time", "schedule__schedule_class", "schedule__teacher", "subtitute_teacher", "reporter")
    permission_required = 'reports.add_report'
    type = "putra"

class PutriSubmitButtonView(SubmitViewMixins):
    form_class = SubmitForm
    template_name = 'reports/report_quick_form-v3.html'
    success_url = reverse_lazy("report-putri-quick-create-v3")
    queryset = Report.objects.select_related("schedule__schedule_course__course", "schedule__schedule_course__teacher", "schedule__schedule_time", "schedule__schedule_class", "schedule__teacher", "subtitute_teacher", "reporter")
    permission_required = 'reports.add_report'
    type = "putri"


class ReportUpdateViewV3(ReportUpdateQuickViewMixin):
    redirect_url = "report-quick-create-v3"
    app_name = "QUICK REPORT V3"
    queryset = Report.objects.select_related("schedule__schedule_course__course", "schedule__schedule_course__teacher", "schedule__schedule_time", "schedule__schedule_class", "schedule__teacher", "subtitute_teacher", "reporter")
    

class ReportUpdatePetugasViewV3(ReportUpdateReporterMixin):
    redirect_url = "report-quick-create-v3"


class ReportDeleteView(BaseModelDeleteView):
    model = Report
    menu_name = 'report'
    permission_required = 'reports.delete_report'
    success_url = reverse_lazy("report-list")


class ReportDeleteAllView(BaseAuthorizedFormView, CreateView):
    model = Report
    menu_name = 'report'
    permission_required = 'reports.delete_report'
    success_url = reverse_lazy("report-list")
    http_method_names = [
        'post'
    ]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        post_data = request.POST.copy()
        selectAll = post_data.get('selectAll')
        if selectAll == 'on':
            data = post_data.pop("selectAll")
            data = post_data.pop("csrfmiddlewaretoken")
            keys_with_on = [key for key, value in post_data.items() if value == 'on']
            Report.objects.filter(pk__in=keys_with_on).delete()
        return HttpResponseRedirect(reverse('report-list'))
    

class ReportUploadView(BaseModelUploadView):
    template_name = 'reports/report_form.html'
    menu_name = "report"
    permission_required = 'reports.create_report'
    success_url = reverse_lazy("report-list")
    model_class = Report


class ReportDownloadExcelView(ModelDownloadExcelView):
    menu_name = 'report'
    permission_required = 'reports.view_report'
    template_name = 'reports/download.html'
    header_names = ['No', 'TANGGAL', 'HARI', 'STATUS', 'JAM KE-', 'KELAS', 'PELAJARAN', 'PENGAJAR', 'GURU PENGGANTI', "PETUGAS PIKET"]
    filename = 'LAPORAN PIKET SMA IT Al Binaa.xlsx'
    queryset = Report.objects.select_related("schedule__schedule_course__course", "schedule__schedule_course__teacher", "schedule__schedule_time", "schedule__schedule_class", "schedule__teacher", "subtitute_teacher", "reporter")

    def get(self, request, *args, **kwargs):
        teacher_id = self.request.GET.get('q')
        month = self.request.GET.get('month', datetime.now().month)
        year = self.request.GET.get('year', datetime.now().year)

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            month = datetime.now().month
            year = datetime.now().year

        if teacher_id:
            qs = self.queryset.filter(schedule__schedule_course__teacher=teacher_id, report_date__month=month, report_date__year=year, status="Hadir").order_by('report_date', 'schedule__schedule_time__number')
            
            if qs.exists():
                data = defaultdict(lambda: {i: 0 for i in range(1, 10)})

                for report in qs:
                    report_date = report.report_date
                    time_number = report.schedule.schedule_time.number
                    data[report_date][time_number] = 1
                
                # hitung jumlah hari dalam bulan
                last_day = calendar.monthrange(year, month)[1]
                all_dates = [
                    date(year, month, day)
                    for day in range(1, last_day + 1)
                ]
                
                # pastikan semua tanggal ada
                ordered_data = {}
                for d in all_dates:
                    if d not in data:
                        data[d] = {i: 0 for i in range(1, 10)}
                        data[d]["Sum"] = 0
                    else:
                        data[d]["Sum"] = sum(data[d][i] for i in range(1, 10))
                    ordered_data[d] = data[d]

                # Hitung total semua jam
                total_jam = sum(row["Sum"] for row in ordered_data.values())

                for tanggal in ordered_data:
                    print(f"{tanggal}: {data[tanggal]}")


                self.individual = True
                self.queryset = ordered_data
                self.teacher = qs.first().schedule.schedule_course.teacher.teacher_name
                self.month = month
                self.year = year
                self.total_jam = total_jam
                self.header_names = ['No', 'TANGGAL'] + [f'JAM KE-{i}' for i in range(1, 10)] + ['TOTAL JAM']
                self.filename = f'LAPORAN PIKET INDIVIDUAL {self.teacher} {calendar.month_name[month]} {year}.xlsx'
            else:
                msg.warning(request, "Data tidak ditemukan untuk guru yang dipilih.")
                return HttpResponseRedirect(reverse('report-individual'))

        return super().get(request, *args, **kwargs)


class ReportIndividualView(BaseAuthorizedModelView, BaseModelQueryListView):
    model = Report
    menu_name = 'report'
    permission_required = 'reports.view_report'
    template_name = 'reports/report_individual.html'
    queryset = Report.objects.select_related("schedule__schedule_course__course", "schedule__schedule_course__teacher", "schedule__schedule_time", "schedule__schedule_class", "schedule__teacher", "subtitute_teacher", "reporter").all()
    paginate_by = 50

    def get_queryset(self):
        teacher_id = self.request.GET.get('q')
        month = self.request.GET.get('month', datetime.now().month)
        year = self.request.GET.get('year', datetime.now().year)

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            month = datetime.now().month
            year = datetime.now().year

        if teacher_id:
            qs = self.queryset.filter(schedule__schedule_course__teacher=teacher_id, report_date__month=month, report_date__year=year).order_by('report_date', 'schedule__schedule_time__number')
            return qs
        return self.queryset.none()
    
    def get_context_data(self, **kwargs):
        month = self.request.GET.get('month', datetime.now().month)
        year = self.request.GET.get('year', datetime.now().year)

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            month = datetime.now().month
            year = datetime.now().year

        import calendar
        month_name = calendar.month_name[month]
        c = super().get_context_data(**kwargs)
        c["teachers"] = Teacher.objects.select_related("user").filter(status="Aktif", gender="L").order_by("teacher_name")
        c["month_name"] = month_name
        c["month"] = month
        c["year"] = year
        return c
        