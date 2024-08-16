from extracurriculars.models import Extracurricular
from django.core.exceptions import PermissionDenied
from files.forms import FileForm
from files.models import File
from typing import Any
from pandas import read_excel, read_csv
from django.db.models.query import QuerySet
from django.shortcuts import HttpResponseRedirect
from django.forms import BaseModelForm
from django.urls import reverse_lazy, reverse
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, FileResponse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from userlog.models import UserLog
from utils.whatsapp import send_WA_create_update_delete, send_WA_general
from students.models import Student
from students.forms import StudentForm
from io import BytesIO
import xlsxwriter


class StudentIndexView(ListView):
    model = Student
    queryset = Student.objects.filter(student_status="Aktif")

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    success_url = reverse_lazy("student-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Input Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.obj = form.save(commit=False)
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="STUDENT",
                message=f"berhasil menambahkan data santri {self.obj}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'data santri {self.obj}', 'students/')
        messages.success(self.request, "Input Data Berhasil! :)")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Create"
        return c
    

class StudentQuickUploadView(LoginRequiredMixin, CreateView):
    model = File
    form_class = FileForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy("student-create")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        df = read_excel(self.object.file, na_filter=False, dtype={"NIS": str, "NISN": str, "NOMOR_HP": str})
        row, _ = df.shape
        for i in range(row):
            try:
                Student.objects.update_or_create(
                    nis = df.iloc[i, 0],
                    nisn = df.iloc[i, 1],
                    nama_siswa = df.iloc[i, 2],
                    defaults=dict(
                        kelas = df.iloc[i, 3],
                        jenis_kelamin = df.iloc[i, 4],
                        alamat = df.iloc[i, 5],
                        tempat_lahir = df.iloc[i, 6],
                        tanggal_lahir = df.iloc[i, 7],
                        email = df.iloc[i, 8],
                        nomor_hp = df.iloc[i, 9],
                        status = df.iloc[i, 10],
                        foto = df.iloc[i, 11],
                    )
                )
            except:
                messages.error(self.request, "Data pada Excel TIDAK SESUAI FORMAT! Mohon sesuaikan dengan format yang ada. Hubungi Administrator jika kesulitan.")
                return HttpResponseRedirect(reverse("student:student-quick-create"))
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="STUDENT",
                message="berhasil impor file Excel data santri"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'impor file Excel', 'data santri', 'students/')
        messages.success(self.request, "Import Data Excel Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Import Excel"
        return c
    

class StudentQuickCSVUploadView(LoginRequiredMixin, CreateView):
    model = File
    form_class = FileForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy("student-create")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        df = read_csv(self.object.file, na_filter=False, dtype={"NIS": str, "NISN": str, "NOMOR_HP": str})
        row, _ = df.shape
        for i in range(row):
            try:
                Student.objects.update_or_create(
                    nis = df.iloc[i, 0],
                    nisn = df.iloc[i, 1],
                    nama_siswa = df.iloc[i, 2],
                    defaults=dict(
                        kelas =df.iloc[i, 3],
                        jenis_kelamin = df.iloc[i, 4],
                        alamat = df.iloc[i, 5],
                        tempat_lahir = df.iloc[i, 6],
                        tanggal_lahir = df.iloc[i, 7],
                        email = df.iloc[i, 8],
                        nomor_hp = df.iloc[i, 9],
                        status = df.iloc[i, 10],
                        foto = df.iloc[i, 11],
                    )
                )
            except:
                messages.error(self.request, "Data pada CSV TIDAK SESUAI FORMAT! Mohon sesuaikan dengan format yang ada. Hubungi Administrator jika kesulitan.")
                return HttpResponseRedirect(reverse("student:student-quick-create-csv"))
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="STUDENT",
                message="berhasil impor file CSV data santri"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'impor file CSV', 'data santri', 'students/')
        messages.success(self.request, "Import Data CSV Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Import Excel"
        return c
    

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    success_url = reverse_lazy("student-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, "Update Data Gagal! :( Ada kesalahan input!")
        return super().form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.obj = form.save(commit=False)
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="UPDATE",
                app="STUDENT",
                message=f"berhasil update data santri {self.obj}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'update', f'data santri {self.obj}', 'students/')
        messages.success(self.request, "Update Data Berhasil! :)")
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Update"
        return c

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    success_url = reverse_lazy("student-list")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.obj = self.get_object()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="DELETE",
                app="STUDENT",
                message=f"berhasil menghapus data santri {self.obj}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'data santri {self.obj}', 'students/')
        messages.success(self.request, "Data Berhasil Dihapus! :)")
        return super().post(request, *args, **kwargs)


class ActiveStudentListView(ListView):
    model = Extracurricular
    template_name = "students/student_active_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        return Extracurricular.objects.prefetch_related("members").filter(members__isnull=False).values("name", "members__student_name", "members__student_class").order_by("members__student_class", "members__student_name", "name")


class NonActiveStudentListView(ListView):
    model = Student
    template_name = "students/student_nonactive_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        active_students = Extracurricular.objects.select_related('members').values_list('members', flat=True).filter(members__isnull=False).distinct()
        return Student.objects.filter(student_status="Aktif").exclude(id__in=active_students).order_by("student_class", "student_name")
    

class DownloadExcelActiveStudent(LoginRequiredMixin, ListView):
    model = Student


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        active_students = Extracurricular.objects.select_related('members').values('name', 'members__student_name', 'members__student_class').filter(members__isnull=False).distinct()
        print(active_students)
        
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()
        merge_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        })
        worksheet.merge_range("A1:D1", 'List Santri Aktif Ekstrakurikuler/SC', merge_format)
        worksheet.write_row(1, 0, ['No', 'Nama Santri', 'Kelas', 'Ekskul/SC'])
        row = 2
        col = 0
        for data in active_students:
            worksheet.write_row(row, col, [row-1, data.get("members__student_name"), data.get("members__student_class"), data.get("name")])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)

        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DOWNLOAD",
            app="STUDENT",
            message="Berhasil download data santri aktif ekskul dalam format Excel"
        )
        send_WA_general(request.user.teacher.phone, 'download', 'data santri aktif ekskul')

        return FileResponse(buffer, as_attachment=True, filename='Santri Aktf Ekskul SMA IT Al Binaa.xlsx')
    

class DownloadExcelInactiveStudent(LoginRequiredMixin, ListView):
    model = Student


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        active_students = Extracurricular.objects.select_related('members').values_list('members', flat=True).filter(members__isnull=False).distinct()
        inactive_students = Student.objects.filter(student_status="Aktif").exclude(id__in=active_students).order_by("student_class", "student_name")
        
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()
        merge_format = workbook.add_format({
            "bold": 1,
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        })
        worksheet.merge_range("A1:C1", 'List Santri Tidak Mengikuti Kegiatan Ekstrakurikuler/SC', merge_format)
        worksheet.write_row(1, 0, ['No', 'Nama Santri', 'Kelas'])
        row = 2
        col = 0
        for data in inactive_students:
            worksheet.write_row(row, col, [row-1, data.student_name, data.student_class])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)

        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DOWNLOAD",
            app="STUDENT",
            message="Berhasil download data santri tidak aktif ekskul dalam format Excel"
        )
        send_WA_general(request.user.teacher.phone, 'download', 'data santri tidak aktif ekskul')
        return FileResponse(buffer, as_attachment=True, filename='Santri Nonaktif Ekskul SMA IT Al Binaa.xlsx')