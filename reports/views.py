from datetime import datetime
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
from utils_piket.mixins import BaseAuthorizedFormView, BaseModelDateBasedListView, BaseModelDeleteView, BaseModelUploadView, BaseAuthorizedModelView, ModelDownloadExcelView, BaseModelQueryListView, QuickReportMixin, ReportUpdateQuickViewMixin, ReportUpdateReporterMixin, SubmitViewMixins
from utils_piket.validate_datetime import get_day
from utils_piket.whatsapp_albinaa import send_whatsapp_group, send_whatsapp_report
# Create your views here.
    
class ReportListView(BaseAuthorizedModelView, BaseModelDateBasedListView):
    model = Report
    queryset = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher", "reporter").all()
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


class ReportPutriQuickCreateViewV3(QuickReportMixin):
    model = Report
    menu_name = 'report'
    form_class = ReportFormV2
    template_name = 'reports/report_quick_form-v3.html'
    permission_required = 'reports.add_report'
    type = "putri"
    class_name = [name.short_class_name for name in Class.objects.filter(category="Putri")]


class SubmitButtonView(SubmitViewMixins):
    form_class = SubmitForm
    template_name = 'reports/report_quick_form-v3.html'
    success_url = reverse_lazy("report-quick-create-v3")
    queryset = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher", "reporter").all()
    permission_required = 'reports.add_report'
    type = "putra"

class PutriSubmitButtonView(SubmitViewMixins):
    form_class = SubmitForm
    template_name = 'reports/report_quick_form-v3.html'
    success_url = reverse_lazy("report-putri-quick-create-v3")
    queryset = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher", "reporter").all()
    permission_required = 'reports.add_report'
    type = "putri"


class ReportUpdateViewV3(ReportUpdateQuickViewMixin):
    redirect_url = "report-quick-create-v3"
    app_name = "QUICK REPORT V3"
    queryset = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher", "reporter").all()
    

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
    queryset = Report.objects.select_related("schedule__schedule_course", "schedule__schedule_course__teacher","schedule__schedule_class", "subtitute_teacher", "reporter").all()