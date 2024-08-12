import locale
import datetime
from typing import Any
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

# Create your views here.
class OlympiadFieldIndexView(ListView):
    model = OlympiadField

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                return OlympiadField.objects.select_related("teacher").prefetch_related("members").filter(teacher=self.request.user.teacher)
        return OlympiadField.select_related("teacher").prefetch_related("members").objects.all()


class OlympiadFieldCreateView(LoginRequiredMixin, CreateView):
    model = OlympiadField
    form_class = OlympiadFieldForm
    success_url = reverse_lazy("olympiad-report-create")

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
                message=f"berhasil menambahkan bidang {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'bidang {self.object}', 'olympiads/', f'detail/{self.object.slug}/')
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
                message=f"berhasil mengubah bidang {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'bidang {self.object}', 'olympiads/', f'detail/{self.object.slug}/')
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
                message=f"berhasil menghapus bidang {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'bidang {self.object}', 'olympiads/')
        messages.success(self.request, "Data berhasil dihapus!")
        return super().post(request, *args, **kwargs)
    

class OlympiadFieldDetailView(DetailView):
    model = OlympiadField



class OlympiadReportIndexView(ListView):
    model = OlympiadReport


class OlympiadReportDetailView(DetailView):
    model = OlympiadReport


class OlympiadReportCreateView(LoginRequiredMixin, CreateView):
    model = OlympiadReport
    form_class = OlympiadReportForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in OlympiadField.objects.values_list("teacher", flat=True).distinct() or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="INPUT",
                app="OLYMPIAD REPORT",
                message=f"berhasil menambahkan laporan {self.object}"
            )
            
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'laporan {self.object}', 'olympiads/', f'report/detail/{self.object.id}/')
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
        if request.user.teacher in OlympiadField.objects.values_list("teacher", flat=True).distinct() or request.user.is_superuser:
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
                message=f"berhasil mengubah laporan {self.object}"
            )
            
        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'laporan {self.object}', 'olympiads/', f'report/detail/{self.object.id}/')
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, ada kesalahan pada input data!")
        return super().form_invalid(form)


class OlympiadReportDeleteView(LoginRequiredMixin, DeleteView):
    model = OlympiadReport
    success_url = reverse_lazy('olympiad-report-list')

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in OlympiadField.objects.values_list("teacher", flat=True).distinct() or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        data = self.get_object()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="DELETE",
                app="OLYMPIAD REPORT",
                message=f"berhasil menambahkan laporan {data}"
            )
            
        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'laporan bidang bimbingan {data}', 'olympiads/report/')
        messages.success(self.request, "Data berhasil dihapus!")
        return super().form_valid(form)