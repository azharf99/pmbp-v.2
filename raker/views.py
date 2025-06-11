from typing import Any
from django.core.exceptions import PermissionDenied
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from raker.models import LaporanPertanggungJawaban, ProgramKerja
from raker.forms import LaporanPertanggungJawabanForm, ProgramKerjaForm
from utils.whatsapp import send_WA_create_update_delete


# Create your views here.
class LaporanPertanggungJawabanCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = LaporanPertanggungJawaban
    form_class = LaporanPertanggungJawabanForm
    permission_required = 'raker.add_laporanpertanggungjawaban'
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Input Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'LPJ {self.object}', 'lpj/')
        messages.success(self.request, "Input Data Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Create"
        return c


class LaporanPertanggungJawabanUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = LaporanPertanggungJawaban
    form_class = LaporanPertanggungJawabanForm
    permission_required = 'raker.change_laporanpertanggungjawaban'
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Update Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        send_WA_create_update_delete(self.request.user.teacher.phone, 'update', f'LPJ {self.object}', 'lpj/')
        messages.success(self.request, "Update Data Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Create"
        return c
    
class LaporanPertanggungJawabanDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = LaporanPertanggungJawaban
    success_url = reverse_lazy("lpj")
    permission_required = 'raker.delete_laporanpertanggungjawaban'

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.obj = self.get_object()
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'LPJ {self.obj}', 'lpj/')
        messages.success(self.request, "Data Berhasil Dihapus! :)")
        return super().post(request, *args, **kwargs)


def proker(request):
    return render(request, 'proker.html')

class ProgramKerjaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ProgramKerja
    form_class = ProgramKerjaForm
    permission_required = 'raker.add_programkerja'
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Input Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'LPJ {self.object}', 'lpj/')
        messages.success(self.request, "Input Data Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Create"
        return c


class ProgramKerjaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ProgramKerja
    form_class = ProgramKerjaForm
    permission_required = 'raker.change_programkerja'
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Update Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        send_WA_create_update_delete(self.request.user.teacher.phone, 'update', f'LPJ {self.object}', 'lpj/')
        messages.success(self.request, "Update Data Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Create"
        return c
    
class ProgramKerjaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ProgramKerja
    success_url = reverse_lazy("lpj")
    permission_required = 'raker.delete_programkerja'

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.obj = self.get_object()
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'LPJ {self.obj}', 'lpj/')
        messages.success(self.request, "Data Berhasil Dihapus! :)")
        return super().post(request, *args, **kwargs)