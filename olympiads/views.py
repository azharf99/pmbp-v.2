import locale
import datetime
from typing import Any
from django.conf import settings
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
import pytz
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from olympiads.forms import OlympiadFieldForm, OlympiadReportForm
from olympiads.models import OlympiadField, OlympiadReport
from userlog.models import UserLog
from utils.whatsapp import send_WA_create_update_delete, send_WA_print
from django.utils import timezone

# Create your views here.
class OlympiadFieldIndexView(ListView):
    model = OlympiadField

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                return OlympiadField.objects.select_related("teacher").prefetch_related("members").filter(teacher=self.request.user.teacher)
        return OlympiadField.objects.select_related("teacher").prefetch_related("members")


class OlympiadFieldCreateView(LoginRequiredMixin, CreateView):
    model = OlympiadField
    form_class = OlympiadFieldForm
    success_url = reverse_lazy("olympiad-field-create")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if OlympiadField.objects.filter(field_name=request.POST.get("field_name"), type=request.POST.get("type")).exists():
            messages.error(self.request, "Maaf, nama bidang sudah ada pada daftar!")
            return redirect(reverse("olympiad-field-create"))
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, ada kesalahan pada input data!")
        return super().form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="OLYMPIADS",
                message=f"berhasil menambahkan bidang olimpiade {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'bidang olimpiade {self.object}', 'olympiads/', f'detail/{self.object.slug}/')
        messages.success(self.request, "Data berhasil ditambahkan!")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['form_name'] = 'Create'
        return c
    

class OlympiadFieldUpdateView(LoginRequiredMixin, UpdateView):
    model = OlympiadField
    form_class = OlympiadFieldForm
    

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in OlympiadField.objects.values_list("teacher", flat=True).distinct() or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, ada kesalahan pada input data!")
        return super().form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="UPDATE",
                app="OLYMPIADS",
                message=f"berhasil mengubah bidang olimpiade {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'bidang olimpiade {self.object}', 'olympiads/', f'detail/{self.object.slug}/')
        messages.success(self.request, "Update Data berhasil!")
        return HttpResponseRedirect(self.get_success_url())    
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['form_name'] = 'Update'
        return c


class OlympiadFieldDeleteView(LoginRequiredMixin, DeleteView):
    model = OlympiadField
    success_url = reverse_lazy('olympiad-field-list')

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="DELETE",
                app="OLYMPIADS",
                message=f"berhasil menghapus bidang olimpiade {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'bidang olimpiade {self.object}', 'olympiads/')
        messages.success(self.request, "Data berhasil dihapus!")
        return super().post(request, *args, **kwargs)
    

class OlympiadFieldDetailView(DetailView):
    model = OlympiadField



class OlympiadReportIndexView(ListView):
    model = OlympiadReport

    def get_queryset(self) -> QuerySet[Any]:
        return OlympiadReport.objects.select_related("field_name__teacher").prefetch_related("students", "field_name__members").all()


class OlympiadReportDetailView(DetailView):
    model = OlympiadReport


class OlympiadReportCreateView(LoginRequiredMixin, CreateView):
    model = OlympiadReport
    form_class = OlympiadReportForm
    success_url = reverse_lazy("olympiad-report-create")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher.id in OlympiadField.objects.values_list("teacher", flat=True).distinct() or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="INPUT",
                app="OLYMPIAD REPORT",
                message=f"berhasil menambahkan laporan olimpiade {self.object}"
            )
            
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'laporan olimpiade {self.object}', 'olympiads/', f'report/detail/{self.object.id}/')
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, ada kesalahan pada input data!")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['form_name'] = 'Create'
        return c
    

class OlympiadReportUpdateView(LoginRequiredMixin, UpdateView):
    model = OlympiadReport
    form_class = OlympiadReportForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher.id in OlympiadField.objects.values_list("teacher", flat=True).distinct() or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['form_name'] = 'Update'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="INPUT",
                app="OLYMPIAD REPORT",
                message=f"berhasil mengubah laporan olimpiade {self.object}"
            )
            
        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'laporan olimpiade {self.object}', 'olympiads/', f'report/detail/{self.object.id}/')
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, ada kesalahan pada input data!")
        return super().form_invalid(form)


class OlympiadReportDeleteView(LoginRequiredMixin, DeleteView):
    model = OlympiadReport
    success_url = reverse_lazy('olympiad-report-list')

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher.id in OlympiadField.objects.values_list("teacher", flat=True).distinct() or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        data = self.get_object()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="DELETE",
                app="OLYMPIAD REPORT",
                message=f"berhasil menambahkan laporan olimpiade {data}"
            )
            
        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'laporan olimpiade bidang bimbingan {data}', 'olympiads/report/')
        messages.success(self.request, "Data berhasil dihapus!")
        return super().form_valid(form)


class OlympiadReportPrintView(LoginRequiredMixin, ListView):
    model = OlympiadReport
    template_name = "olympiads/olympiadreport_print.html"

    def get_queryset(self):        
        return OlympiadReport.objects.select_related("field_name").filter(field_name__slug=self.kwargs.get('slug')).order_by('-report_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        locale.setlocale(locale.LC_ALL, 'id_ID')
        context['tahun_ajaran'] = settings.TAHUN_AJARAN
        context['olympiad_field'] = get_object_or_404(OlympiadField, slug=self.kwargs.get("slug"))
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="PRINT",
            app="LAPORAN",
            message=f"berhasil mencetak laporan olimpiade {context['olympiad_field']}"
        )
        send_WA_print(self.request.user.teacher.phone, 'laporan olimpiade', f"{context['olympiad_field']}")
        return context