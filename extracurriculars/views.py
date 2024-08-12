
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from extracurriculars.models import Extracurricular
from extracurriculars.forms import ExtracurricularForm
from students.models import Student
from userlog.models import UserLog
from utils.whatsapp import send_WA_create_update_delete
from typing import Any


# Create your views here.
class ExtracurricularIndexView(ListView):
    model = Extracurricular
    paginate_by = 9

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                return Extracurricular.objects.prefetch_related('teacher', 'members').filter(teacher=self.request.user.teacher).order_by('type', 'name')
        return Extracurricular.objects.prefetch_related('teacher', 'members').order_by('type', 'name')
    

class ExtracurricularDetailView(DetailView):
    model = Extracurricular


class ExtracurricularCreateView(LoginRequiredMixin, CreateView):
    model = Extracurricular
    form_class = ExtracurricularForm
    success_url = reverse_lazy("extracurricular-list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Input Data gagal! Ada kesalahan input.")
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="CREATE",
            app="EKSKUL",
            message=f"Berhasil menambahkan ekskul {self.object}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, "menambahkan", f"ekskul {self.object}", "data/", f"{self.object.slug}/")
        messages.success(self.request, "Input Data Berhasil!")
        return HttpResponseRedirect(self.get_success_url())
    

class ExtracurricularUpdateView(LoginRequiredMixin, UpdateView):
    model = Extracurricular
    form_class = ExtracurricularForm
    success_url = reverse_lazy("extracurricular-list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.id in self.get_object().teacher.values_list(flat=True) or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Input Data gagal! Ada kesalahan input.")
        return super().form_invalid(form)
    
    def form_valid(self, form):
        self.object = form.save()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="UPDATE",
            app="EKSKUL",
            message=f"Berhasil mengubah data ekskul {self.object}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, "mengubah", f"data ekskul {self.object}", "data/", f"{self.object.slug}/")
        messages.success(self.request, "Update Data Berhasil!")
        return HttpResponseRedirect(self.get_success_url())

class ExtracurricularDeleteView(LoginRequiredMixin, DeleteView):
    model = Extracurricular
    success_url = reverse_lazy("extracurricular-list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        ekskul = self.get_object()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="DELETE",
            app="EKSKUL",
            message=f"Berhasil menghapus data ekskul {ekskul}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, "menghapus", f"data ekskul {ekskul}", "data/", f"{ekskul.slug}/")
        messages.success(self.request, "Data Berhasil Dihapus!")
        return super().post(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_name'] = "Ekstrakurikuler/SC"
        return context
    