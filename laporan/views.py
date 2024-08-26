import locale
from typing import Any
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from laporan.models import Report
from laporan.forms import ReportForm
from extracurriculars.models import Extracurricular
from userlog.models import UserLog
from utils.wa import send_WA_create_update_delete, send_WA_print
from django.conf import settings

class ReportIndexView(ListView):
    model = Report
    paginate_by = 12

    def get_queryset(self) -> QuerySet[Any]:
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            return Report.objects.select_related("extracurricular").prefetch_related("students",  "teacher").filter(teacher=self.request.user.teacher)
        return Report.objects.select_related("extracurricular").prefetch_related("students", "teacher").all()


class ReportDetailView(DetailView):
    model = Report


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    success_url = reverse_lazy("report-create")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher.id in Extracurricular.objects.values_list('teacher', flat=True).distinct() or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if Report.objects.select_related("extracurricular", "teacher")\
            .filter(report_date=request.POST.get("report_date"), extracurricular=request.POST.get("extracurricular"))\
            .exists():
            messages.error(self.request, "Laporan untuk tanggal ini sudah ada. Silahkan pilih tanggal lain")
            return redirect(reverse("report-create"))
        return super().post(request, *args, **kwargs)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error! Input data ada yang salah.")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="CREATE",
            app="LAPORAN",
            message=f"berhasil menambahkan data laporan ekskul/sc {self.object}"
        )
        
        send_WA_create_update_delete(self.request.user.teacher.phone, f'{self.request.user.teacher} menambahkan', f'laporan pertemuan Ekskul/SC {self.object}', 'laporan/', f'{self.object.id}/')
        messages.success(self.request, "Input Laporan berhasil!")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        data = Extracurricular.objects.prefetch_related("teacher", "members").filter(teacher=self.request.user.teacher)
        teacher_set = []
        context["extracurricular"] = data
        teacher = [[teacher_set.append(i) if not teacher_set.__contains__(i) else i for i in datum.teacher.all()] for datum in data]
        context["teacher"] = teacher_set
        context["filtered_student"] = Extracurricular.objects.prefetch_related("teacher", "members").filter(teacher=self.request.user.teacher).values("members", "members__student_name", "members__student_class").order_by("members").distinct()
        context["form_name"] = "Create"
        return context


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    form_class = ReportForm
    success_url = reverse_lazy("report-list")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in self.get_object().teacher.all() or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error! Input data ada yang salah.")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="UPDATE",
            app="LAPORAN",
            message=f"berhasil mengubah data laporan pertemuan ekskul {self.object}"
        )

        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'laporan pertemuan Ekskul/SC {self.object}', 'laporan/', f'{self.object.id}/')
        messages.success(self.request, "Input Laporan berhasil!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["filtered_student"] = Extracurricular.objects.prefetch_related("teacher", "members").filter(teacher=self.request.user.teacher).values("members").order_by("members")
        context["form_name"] = "Update"
        return context


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = Report
    success_url = reverse_lazy("report-list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in self.get_object().teacher.all() or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        obj = self.get_object()
        
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="DELETE",
            app="LAPORAN",
            message=f"berhasil menghapus data laporan pertemuan ekskul {obj}"
        )

        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'laporan pertemuan Ekskul/SC {obj}', 'laporan/', f'{obj.id}/')
        messages.success(self.request, "Input Laporan berhasil!")
        return super().post(request, *args, **kwargs)
    


class PrintToPrintView(LoginRequiredMixin, ListView):
    model = Report
    template_name = "laporan/report_print.html"

    def get_queryset(self):
        if self.request.GET.get('month'):
            if self.request.GET.get('year'):
                return Report.objects.filter(extracurricular__slug=self.kwargs.get('slug'), report_date__month=self.request.GET.get('month'), report_date__year=self.request.GET.get('year')).order_by('report_date')
            
            return Report.objects.filter(extracurricular__slug=self.kwargs.get('slug'), report_date__month=self.request.GET.get('month'), report_date__year=timezone.now().year).order_by('report_date')
        
        return Report.objects.filter(extracurricular__slug=self.kwargs.get('slug'), report_date__month=timezone.now().month-1).order_by('report_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        locale.setlocale(locale.LC_ALL, 'id_ID')
        context['tahun_ajaran'] = settings.TAHUN_AJARAN
        context['extracurricular'] = get_object_or_404(Extracurricular, slug=self.kwargs.get("slug"))
        context['students'] = Extracurricular.objects.filter(slug=self.kwargs.get('slug')).order_by('members').values_list('members__student_name', 'members__student_class')
        context['angka'] = [x for x in range(15)]
        ekskul = get_object_or_404(Extracurricular, slug=self.kwargs.get('slug'))
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="PRINT",
            app="LAPORAN",
            message=f"berhasil mencetak laporan pertemuan ekskul {ekskul}"
        )
        send_WA_print(self.request.user.teacher.phone, 'laporan pertemuan Ekskul/SC', f"{ekskul}")
        return context


class ReportOptionsView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'laporan/report_options.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = Report.objects.filter(extracurricular__slug=self.kwargs.get("slug")).values('report_date__month', 'report_date__year').order_by().distinct()
        monthName = {0: "Bulan", 1:"Januari", 2:"Februari", 3:"Maret", 4:"April", 5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus", 9:"September", 10:"Oktober", 11:"November", 12:"Desember"}

        monthList = list()
        monthSet = set()
        yearSet = set()
        allDict = dict()
        for i in data:
                monthSet.add(i['report_date__month'])
                yearSet.add(i['report_date__year'])
        for i in monthSet:
            monthList.append({"nama": monthName.get(i), "value": i})
        allDict["month"] = monthList
        allDict["year"] = list(yearSet)
        if len(data) > 0 :
            context["object_list"] = [allDict]
        else:
            context["object_list"] = None
        context["slug"] = self.kwargs.get("slug")
        context["show_type"] = "options"
        return context
    
# class ReportEkskulPrintView(LoginRequiredMixin, ListView):
#     model = Report
#     template_name = "laporan-print2.html"

#     def get_queryset(self) -> QuerySet[Any]:
#         return Report.objects.select_related("extracurricular", "teacher")\
#             .filter(extracurricular__slug=self.kwargs.get("slug")).order_by('report_date')

#     def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
#         obj = get_object_or_404(Extracurricular, slug=self.kwargs.get("slug"))
#         UserLog.objects.create(
#             user=request.user.teacher,
#             action_flag="PRINT",
#             app="LAPORAN",
#             message=f"berhasil mencetak laporan pertemuan ekskul {obj}"
#         )
#         send_WA_print(self.request.user.teacher.phone, 'laporan pertemuan Ekskul/SC', f"{obj}")
#         return super().get(request, *args, **kwargs)

#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context = super().get_context_data(**kwargs)
#         context["ekskul"] = get_object_or_404(Extracurricular, slug=self.kwargs.get("slug"))
#         return context


