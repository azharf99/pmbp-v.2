from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, FileResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from utils.whatsapp import send_WA_create_update_delete
from io import BytesIO
from prestasi.forms import PrestasiForm, ProgramPrestasiForm
from prestasi.models import Prestasi, ProgramPrestasi
from userlog.models import UserLog
from typing import Any
from xlsxwriter import Workbook
from django.conf import settings


# Create your views here.
class PrestasiIndexView(ListView):
    model = Prestasi
    queryset = Prestasi.objects.filter(created_at__gt=settings.TANGGAL_TAHUN_AJARAN)
    paginate_by = 9

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["tahun_ajaran"] = settings.TAHUN_AJARAN
        return c


class PrestasiDetailView(DetailView):
    model = Prestasi


class PrestasiCreateView(LoginRequiredMixin, CreateView):
    model = Prestasi
    form_class = PrestasiForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, Ada kesalahan pada input data anda!")
        return super().form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="PRESTASI",
                message=f"berhasil menambahkan data prestasi {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f' Prestasi {self.object}', 'prestasi/', f'detail/{self.object.id}/')
        messages.success(self.request, "Data berhasil ditambahkan!")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_view"] = "Create"
        return c


class PrestasiUpdateView(LoginRequiredMixin, UpdateView):
    model = Prestasi
    form_class = PrestasiForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, Ada kesalahan pada input data anda!")
        return super().form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = self.get_object()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="UPDATE",
                app="PRESTASI",
                message=f"berhasil mengubah data prestasi {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f' Prestasi {self.object}', 'prestasi/', f'detail/{self.object.id}/')
        messages.success(self.request, "Data berhasil diupdate!")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_view"] = "Update"
        return c
    
class PrestasiDeleteView(LoginRequiredMixin, DeleteView):
    model = Prestasi
    success_url = reverse_lazy("prestasi-list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        data = self.get_object()
        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DELETE",
            app="PRESTASI",
            message=f"berhasil menghapus data prestasi {data}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f' Prestasi {data}', 'prestasi/')
        messages.success(self.request, "Data berhasil dihapus!")
        return super().post(request, *args, **kwargs)
    

class PretasiPrintExcelView(ListView):
    model = Prestasi
    queryset = Prestasi.objects.all()
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
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
        worksheet.merge_range("A1:L1", "Data Prestasi SMA IT AL BINAA", merge_format)
        worksheet.write_row(1, 0, ['No', 'Peraih Prestasi', 'Kelas', 'Kategori Lomba', 'Jenis Lomba', 'Tingkat Lomba', 'Tahun Lomba', 'Nama Lomba', 'Bidang Lomba', 'Predikat', 'Penyelengggara', 'Sekolah'], title_format)
        row = 2
        col = 0
        for data in self.queryset:
            worksheet.write_row(row, col, [row, data.awardee, data.awardee_class, data.category, data.type, data.level, data.year, data.name, data.field, data.predicate, data.organizer, data.school])
            row += 1

        worksheet.autofit()
        workbook.close()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename='Prestasi SMA IT Al Binaa.xlsx')


class PrestasiPrintExcelThisYearView(ListView):
    model = Prestasi
    queryset = Prestasi.objects.filter(created_at__gt=settings.TANGGAL_TAHUN_AJARAN)
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
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
        worksheet.merge_range("A1:L1", f"Data Prestasi SMA IT AL BINAA T.A. {settings.TAHUN_AJARAN}", merge_format)
        worksheet.write_row(1, 0, ['No', 'Peraih Prestasi', 'Kelas', 'Kategori Lomba', 'Jenis Lomba', 'Tingkat Lomba', 'Tahun Lomba', 'Nama Lomba', 'Bidang Lomba', 'Predikat', 'Penyelengggara', 'Sekolah'], title_format)
        row = 2
        col = 0
        worksheet.autofit()
        for data in self.queryset:
            worksheet.write_row(row, col, [row, data.awardee, data.awardee_class, data.category, data.type, data.level, data.year, data.name, data.field, data.predicate, data.organizer, data.school])
            row += 1

        worksheet.autofit()
        workbook.close()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename='Prestasi TA. 2024-2025 SMA IT Al Binaa.xlsx')
    


class ProgramPrestasiIndexView(ListView):
    model = ProgramPrestasi
    queryset = ProgramPrestasi.objects.filter(tanggal__gt=settings.TANGGAL_TAHUN_AJARAN).order_by('-created_at', '-tanggal',)
    paginate_by = 10

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["tahun_ajaran"] = settings.TAHUN_AJARAN
        return c

class ProgramPrestasiDetailView(DetailView):
    model = ProgramPrestasi


class ProgramPrestasiCreateView(LoginRequiredMixin, CreateView):
    model = ProgramPrestasi
    form_class = ProgramPrestasiForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, Ada kesalahan pada input data anda!")
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="PROGRAM PRESTASI",
                message=f"berhasil menambahkan data program prestasi {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'Program Prestasi {self.object}', 'prestasi/program/')
        messages.success(self.request, "Data berhasil ditambahkan!")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_view"] = "Create"
        return c


class ProgramPrestasiUpdateView(LoginRequiredMixin, UpdateView):
    model = ProgramPrestasi
    form_class = ProgramPrestasiForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Error, Ada kesalahan pada input data anda!")
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="UPDATE",
                app="PROGRAM PRESTASI",
                message=f"berhasil mengubah data program prestasi {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'Program Prestasi {self.object}', 'prestasi/program/')
        messages.success(self.request, "Data berhasil diupdate!")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_view"] = "Update"
        return c

class ProgramPrestasiDeleteView(LoginRequiredMixin, DeleteView):
    model = ProgramPrestasi
    success_url = reverse_lazy("program-prestasi-list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        data = self.get_object()
        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DELETE",
            app="PRESTASI_DOKUMENTASI",
            message=f"berhasil menghapus program prestasi {data}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'Program Prestasi {data}', 'prestasi/program/')
        return super().post(request, *args, **kwargs)
    

class ProgramPrestasiPrintExcelThisYearView(ListView):
    model = ProgramPrestasi
    queryset = ProgramPrestasi.objects.filter(tanggal__gt=settings.TANGGAL_TAHUN_AJARAN).order_by('-tanggal', 'program_prestasi')
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = Workbook(buffer)
        worksheet = workbook.add_worksheet()
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
        worksheet.merge_range("A1:F1", "Program Prestasi SMA IT Al Binaa Tahun Ajaran 2024-2025", merge_format)
        worksheet.merge_range("A2:F2", f"Tahun Ajaran {settings.TAHUN_AJARAN}", merge_format)

        worksheet.write_row(3, 0, ['No', 'Program Prestasi', 'Tanggal', 'Nama Peserta', 'Kelas Peserta', 'Pencapaian', 'Catatan'], title_format)
        row = 4
        num = 1
        col = 0
        for data in self.queryset:
            for peserta in data.nama_peserta.all():
                worksheet.write_row(row, col, [num, data.program_prestasi, f"{data.tanggal}", peserta.student_name, peserta.student_class, data.pencapaian, data.catatan])
                num += 1
                row += 1

        # Autofit the worksheet.
        worksheet.autofit()
        worksheet.set_column("A:A", 5)
        workbook.close()
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename=f'Program Prestasi SMA IT Al Binaa T.A. {settings.TAHUN_AJARAN_STRIPPED}.xlsx')
