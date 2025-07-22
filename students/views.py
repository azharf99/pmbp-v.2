from django.conf import settings
from xlsxwriter import Workbook
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
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, FileResponse, Http404, HttpResponseNotFound
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from classes.models import Class
from laporan.models import Report
from userlog.models import UserLog
from utils.whatsapp import send_WA_create_update_delete, send_WA_general
from students.models import Student
from students.forms import StudentForm
from io import BytesIO
import xlsxwriter
from django.db.models import Q
from django.utils import timezone


class StudentIndexView(ListView):
    model = Student
    queryset = Student.objects.select_related('student_class').filter(student_status="Aktif")

class StudentLevelUpView(CreateView):
    model = Student
    fields = '__all__'
    template_name = "students/student_level-up.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        query = request.POST.get("query")
        this_year_postfix = str(timezone.now().year)[2:]
        if query == "kelas_12":
            nis_alumni = int(this_year_postfix) - 3

            graduated_students = Student.objects.select_related('student_class').filter(student_status="Aktif", nis__startswith=f"{nis_alumni}")
            if not graduated_students.exists():
                messages.error(request, "Naik Level Kelas 12 ke Alumni Sudah dilakukan!")
                return HttpResponseRedirect(reverse("student-level-up"))

            graduated_students.update(student_status="Lulus")

            messages.success(request, "Naik Level Kelas 12 ke Alumni Berhasil!")
            return HttpResponseRedirect(reverse("student-level-up"))

        elif query == "kelas_11":

            nis_kelas_12 = int(this_year_postfix) - 2
            students_grade_12 = Student.objects.select_related('student_class').filter(student_status="Aktif", nis__startswith=f"{nis_kelas_12}")
            if not students_grade_12.exists():
                messages.error(request, "Naik Level Kelas 12 ke Kelas 12 Sudah dilakukan!")
                return HttpResponseRedirect(reverse("student-level-up"))
            for student in students_grade_12:
                student.student_class = Class.objects.get(class_name=f"XII-MIPA-{student.student_class.class_name[-1]}")

            Student.objects.bulk_update(students_grade_12, ['student_class'])

            messages.success(request, "Naik Level Kelas 11 ke Kelas 12 Berhasil!")
            return HttpResponseRedirect(reverse("student-level-up"))

        return HttpResponseNotFound("Data tidak valid!")

    

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
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="STUDENT",
                message=f"berhasil menambahkan data santri {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'data santri {self.object}', 'students/')
        messages.success(self.request, "Input Data Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())
    
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
                student_class = Class.objects.get(class_name=df.iloc[i, 3])
                Student.objects.update_or_create(
                    nis = df.iloc[i, 0],
                    defaults=dict(
                        student_name = df.iloc[i, 2],
                        student_class = student_class,
                        gender = df.iloc[i, 4],
                        address = df.iloc[i, 5],
                        student_birth_place = df.iloc[i, 6],
                        student_birth_date = df.iloc[i, 7] or None,
                        email = df.iloc[i, 8],
                        phone = df.iloc[i, 9],
                        student_status = df.iloc[i, 10],
                    )
                )
            except:
                messages.error(self.request, "Data pada Excel TIDAK SESUAI FORMAT! Mohon sesuaikan dengan format yang ada. Hubungi Administrator jika kesulitan.")
                return HttpResponseRedirect(reverse("student-quick-create"))
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
        self.object = form.save()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="UPDATE",
                app="STUDENT",
                message=f"berhasil update data santri {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'update', f'data santri {self.object}', 'students/')
        messages.success(self.request, "Update Data Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())

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
        self.object = self.get_object()
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="DELETE",
                app="STUDENT",
                message=f"berhasil menghapus data santri {self.object}"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'data santri {self.object}', 'students/')
        messages.success(self.request, "Data Berhasil Dihapus! :)")
        return super().post(request, *args, **kwargs)


class ActiveStudentListView(ListView):
    model = Student
    template_name = "students/student_active_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get("query")
        extracurricular = self.request.GET.get("extracurricular")

        if extracurricular:
            members = Extracurricular.objects.prefetch_related('members', 'teacher').filter(slug=extracurricular)[0].members.all()
            data = Report.objects.select_related('extracurricular', 'teacher').prefetch_related('students').filter(extracurricular__slug=extracurricular, report_date__month=timezone.now().month)
            for i in data:
                datum = members.difference(i.students.all())
        if query:
            data = Student.objects.select_related('student_class').prefetch_related('extracurricular_set', 'report_set__extracurricular', 'report_set__students').filter(Q(student_status="Aktif") & Q(student_name__icontains=query)).all()
            if data.exists():
                messages.success(self.request, f"{len(data)} Data Berhasil Ditemukan!")
            else:
                messages.error(self.request, "Data Tidak Ditemukan!")
            return data
        
        return Student.objects.select_related('student_class').filter(student_status="Aktif").prefetch_related('extracurricular_set', 'report_set__extracurricular', 'report_set__students').all()


class NonActiveStudentListView(ListView):
    model = Student
    template_name = "students/student_nonactive_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        active_students = Extracurricular.objects.select_related('members', 'teacher').values_list('members', flat=True).filter(members__isnull=False).distinct()
        return Student.objects.select_related('student_class').filter(student_status="Aktif").exclude(id__in=active_students).order_by("student_class__class_name", "student_name")
    

class DownloadExcelActiveStudent(LoginRequiredMixin, ListView):
    model = Student


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        active_students = Extracurricular.objects.select_related('members').values('name', 'members__student_name', 'members__student_class').filter(members__isnull=False).distinct()
        
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
        inactive_students = Student.objects.select_related('student_class').filter(student_status="Aktif").exclude(id__in=active_students).order_by("student_class__class_name", "student_name")
        
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
            worksheet.write_row(row, col, [row-1, data.student_name, data.student_class.class_name])
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


class StudentPrivateView(ListView):
    model = Student
    template_name = "students/student_private_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        return Student.objects.prefetch_related("student_class")
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        month_now, year_now = timezone.now().month, timezone.now().year
        month_query = self.request.GET.get("month", default=f'{month_now}')
        year_query = self.request.GET.get("year", default=f'{year_now}')
        try:
            month = int(month_query) if 0 < int(month_query) <= 12 else month_now
            year = int((year_query)) if 0 < int(month_query) <= 9999 else year_now
        except:
            month = month_now
            year = year_now
        
        object_list = self.get_queryset()
        for obj in object_list:
            obj.filtered_private_set = obj.private_set.filter(
                    tanggal_bimbingan__month=month,
                    tanggal_bimbingan__year=year
            )
        c["filtered_object_list"] = object_list
        c["month"] = str(month)
        c["year"] = str(year)
        return c
    
class DownloadPrivateListView(ListView):
    model = Student
    queryset = Student.objects.filter(student_status="Aktif")

    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:

            month_now, year_now = timezone.now().month, timezone.now().year
            month_query = self.request.GET.get("month", default=f'{month_now}')
            year_query = self.request.GET.get("year", default=f'{year_now}')
            try:
                month = int(month_query) if 0 < int(month_query) <= 12 else month_now
                year = int((year_query)) if 0 < int(month_query) <= 9999 else year_now
            except:
                month = month_now
                year = year_now
            object_list = self.get_queryset()
            for obj in object_list:
                obj.filtered_private_set = obj.private_set.filter(
                        tanggal_bimbingan__month=month,
                        tanggal_bimbingan__year=year
                )

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
            worksheet.merge_range("A1:F1", "Daftar Kehadiran Privat Santri SMAS IT AL BINAA", merge_format)
            worksheet.merge_range("A2:F2", f"Tahun Ajaran {settings.TAHUN_AJARAN}", merge_format)

            worksheet.write_row(3, 0, ['No', 'Nama Santri', 'Kelas', 'Mata Pelajaran', 'Pengajar', 'Tanggal Kehadiran'], title_format)
            row = 4
            num = 1
            col = 0
            for data in object_list:
                for private in data.filtered_private_set.all():
                    worksheet.write_row(row, col, [num, data.student_name, data.student_class.class_name, f"{private.pelajaran}", f"{private.pembimbing}", f"{private.tanggal_bimbingan}"])
                    num += 1
                    row += 1

            # Autofit the worksheet.
            worksheet.autofit()
            worksheet.set_column("A:A", 5)
            workbook.close()
            buffer.seek(0)

            monthName = {0: "Bulan", 1:"Januari", 2:"Februari", 3:"Maret", 4:"April", 5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus", 9:"September", 10:"Oktober", 11:"November", 12:"Desember"}
            try:
                monthData = monthName.get(int(month))
            except:
                monthData = "Error"

            UserLog.objects.create(
                user=request.user.teacher,
                action_flag="DOWNLOAD",
                app="PRIVATE",
                message="Berhasil download data privat santri dalam format Excel"
            )

            return FileResponse(buffer, as_attachment=True, filename=f'Privat Santri {monthData} {year} SMA IT Al Binaa T.A. {settings.TAHUN_AJARAN_STRIPPED}.xlsx')
        
        raise PermissionDenied