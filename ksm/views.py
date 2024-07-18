import locale
import datetime
from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpResponse
import pytz

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from ksm.models import BidangKSM, SiswaKSM, LaporanKSM
from userlog.models import UserLog
from dashboard.whatsapp import send_whatsapp_input_anggota, send_whatsapp_laporan_osn

# Create your views here.
class KsmIndexView(ListView):
    model = BidangKSM
    context_object_name = 'data'
    template_name = 'new_ksm.html'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return BidangKSM.objects.all().order_by('nama_bidang')
            elif self.request.user.teacher.bidangosn_set.count() > 0:
                return BidangKSM.objects.filter(pembimbing=self.request.user.teacher).order_by('nama_bidang')
            else:
                return BidangKSM.objects.all().order_by('nama_bidang')
        else:
            return BidangKSM.objects.all().order_by('nama_bidang')


class CreateBidangKsmView(LoginRequiredMixin, CreateView):
    model = BidangKSM
    fields = '__all__'
    login_url = '/login/'
    template_name = 'new_osn-input.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Data berhasil disimpan!")
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="INPUT",
                app="KSM",
                message="Berhasil input bidang KSM"
            )
        send_whatsapp_input_anggota(self.request.user.teacher.no_hp, 'KSM', 'bidang KSM', 'KSM', 'input nama')
        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)

class UpdateBidangKsmView(LoginRequiredMixin, UpdateView):
    model = BidangKSM
    fields = '__all__'
    login_url = '/login/'
    template_name = 'new_osn-input.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Data berhasil disimpan!")
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="EDIT",
                app="ksm",
                message="Berhasil edit bidang ksm"
            )
        send_whatsapp_input_anggota(self.request.user.teacher.no_hp, 'KSM', 'bidang ksm', 'ksm', 'mengubah')
        return super().form_valid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)


class DeleteBidangKsmView(LoginRequiredMixin, DeleteView):
    model = BidangKSM
    login_url = '/login/'
    success_url = reverse_lazy('ksm:ksm-index')
    template_name = 'new_osn-delete.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Data berhasil disimpan!")
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="DELETE",
                app="ksm",
                message="Berhasil hapus bidang ksm"
            )
        send_whatsapp_input_anggota(self.request.user.teacher.no_hp, 'KSM', 'bidang ksm', 'ksm', 'menghapus')
        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)
    

class DetailBidangKSMView(DetailView):
    model = BidangKSM
    template_name = 'new_osn-detail.html'
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_siswa'] = SiswaKSM.objects.filter(bidang_ksm__slug=self.kwargs.get('slug')).order_by('nama_siswa__kelas', 'nama_siswa__nama_siswa')
        context['data_laporan'] = LaporanKSM.objects.filter(bidang_ksm__slug=self.kwargs.get('slug')).order_by('tanggal_pembinaan')
        return context

class CreateSiswaKsmView(LoginRequiredMixin, CreateView):
    model = SiswaKSM
    fields = '__all__'
    login_url = '/login/'
    template_name = 'new_osn-input.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="INPUT",
                app="ksm",
                message="Berhasil menambahkan siswa ke bidang ksm"
            )
        send_whatsapp_input_anggota(self.request.user.teacher.no_hp, 'KSM', 'siswa ksm', 'ksm', f'menambahkan siswa ke')
        return super().form_valid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)

class UpdateSiswaKsmView(LoginRequiredMixin, UpdateView):
    model = SiswaKSM
    fields = '__all__'
    login_url = '/login/'
    template_name = 'new_osn-input.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="EDIT",
                app="ksm",
                message="Berhasil mengubah siswa ke bidang ksm"
            )
        send_whatsapp_input_anggota(self.request.user.teacher.no_hp, 'KSM', 'siswa ksm', 'ksm', f'mengubah siswa ke')
        return super().form_valid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)


class DeleteSiswaKsmView(LoginRequiredMixin, DeleteView):
    model = SiswaKSM
    login_url = '/login/'
    success_url = reverse_lazy('ksm:ksm-index')
    template_name = 'new_osn-delete.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="DELETE",
                app="ksm",
                message="Berhasil menghapus siswa ke bidang ksm"
            )
        send_whatsapp_input_anggota(self.request.user.teacher.no_hp, 'KSM', 'siswa ksm', 'ksm', f'menghapus siswa ke')
        return super().form_valid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)
    

class CreateLaporanKsmView(LoginRequiredMixin, CreateView):
    model = LaporanKSM
    fields = '__all__'
    login_url = '/login/'
    template_name = 'new_osn-input.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        tanggal = datetime.date.fromisoformat(str(self.request.POST.get('tanggal_pembinaan'))).strftime('%d %B %Y')
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="INPUT",
                app="KSM",
                message="Berhasil menambahkan laporan KSM untuk tanggal"
            )
            
        send_whatsapp_laporan_osn(self.request.user.teacher.no_hp, 'KSM', 'input', tanggal)
        return super().form_valid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)

class UpdateLaporanKsmView(LoginRequiredMixin, UpdateView):
    model = LaporanKSM
    fields = '__all__'
    login_url = '/login/'
    template_name = 'new_osn-input.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        tanggal = datetime.date.fromisoformat(str(self.request.POST.get('tanggal_pembinaan'))).strftime('%d %B %Y')
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="EDIT",
                app="KSM",
                message="Berhasil mengubah laporan KSM untuk tanggal"
            )
            
        send_whatsapp_laporan_osn(self.request.user.teacher.no_hp, 'KSM', 'edit', tanggal)
        return super().form_valid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)


class DeleteLaporanKsmView(LoginRequiredMixin, DeleteView):
    model = LaporanKSM
    login_url = '/login/'
    success_url = reverse_lazy('ksm:ksm-index')
    template_name = 'new_osn-delete.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        return c
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        tanggal = datetime.date.fromisoformat(str(self.request.POST.get('tanggal_pembinaan'))).strftime('%d %B %Y')
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="DELETE",
                app="KSM",
                message="Berhasil menambahkan laporan KSM untuk tanggal"
            )
            
        send_whatsapp_laporan_osn(self.request.user.teacher.no_hp, 'KSM', 'hapus', tanggal)
        return super().form_valid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Yang kamu isi ada yang salah. Mohon cek ulang.")
        return super().form_invalid(form)


class PrintKSMReport(ListView):
    model = LaporanKSM
    template_name = 'ksm-print.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c['name'] = 'KSM'
        c['angka']= [x for x in range(15)]
        c['level']= "KABUPATEN"
        c['tag']= "KSM"
        c['data']= get_object_or_404(BidangKSM, slug=self.kwargs.get('slug'))
        c['data_siswa']= SiswaKSM.objects.filter(bidang_ksm__slug=self.kwargs.get('slug')).order_by('nama_siswa__kelas', 'nama_siswa__nama')
        c['data_laporan']= LaporanKSM.objects.filter(bidang_ksm__slug=self.kwargs.get('slug')).order_by('tanggal_pembinaan')
        c['tanggal']= datetime.datetime.now(pytz.timezone('Asia/Jakarta'))
        return c




# def cetak_laporan_osnk(request, slug):
#     locale.setlocale(locale.LC_ALL, 'id_ID')
#     tanggal = datetime.datetime.now(pytz.timezone('Asia/Jakarta'))
#     data = get_object_or_404(BidangOSN, slug=slug)
#     data_siswa = SiswaOSN.objects.filter(bidang_osn__slug=slug).order_by('nama_siswa__kelas', 'nama_siswa__nama')
#     data_laporan = LaporanOSN.objects.filter(bidang_osn__nama_bidang=data.nama_bidang).filter(tanggal_pembinaan__lt="2024-03-03").order_by('tanggal_pembinaan')
#     # angka = [x for x in range(15)]
#     UserLog.objects.create(
#                 user="Seseorang",
#                 action_flag="CETAK",
#                 app="OSN",
#                 message="Berhasil mencetak laporan OSN-K {}".format(data.nama_bidang)
#     )
#     context = {
#         # 'angka': angka,
#         'level': "KABUPATEN",
#         'tag': "OSN-K",
#         'data': data,
#         'data_siswa': data_siswa,
#         'data_laporan': data_laporan,
#         'tanggal': tanggal,
#     }
#     return render(request, 'osn-print.html', context)

# def cetak_laporan_osnp(request, slug):
#     locale.setlocale(locale.LC_ALL, 'id_ID')
#     tanggal = datetime.datetime.now(pytz.timezone('Asia/Jakarta'))
#     data = get_object_or_404(BidangOSN, slug=slug)
#     data_siswa = SiswaOSN.objects.filter(bidang_osn__slug=slug).order_by('nama_siswa__kelas', 'nama_siswa__nama')
#     data_laporan = LaporanOSN.objects.filter(bidang_osn__nama_bidang=data.nama_bidang).filter(tanggal_pembinaan__gt="2024-03-03").filter(tanggal_pembinaan__lt="2023-06-09").order_by('tanggal_pembinaan')
#     # angka = [x for x in range(15)]
#     UserLog.objects.create(
#                 user="Seseorang",
#                 action_flag="CETAK",
#                 app="OSN",
#                 message="Berhasil mencetak laporan OSN-P {}".format(data.nama_bidang)
#     )
#     context = {
#         'level': "PROVINSI",
#         'tag': "OSN-P",
#         'data': data,
#         'data_siswa': data_siswa,
#         'data_laporan': data_laporan,
#         'tanggal': tanggal,
#     }
#     return render(request, 'osn-print.html', context)