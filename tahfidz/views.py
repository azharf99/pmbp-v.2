from datetime import datetime
from django.utils import timezone
from django.db.models import Count
from typing import Any
from django.conf import settings
from django.core.exceptions import PermissionDenied, BadRequest
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from pandas import read_csv, read_excel
from classes.models import Class
from files.forms import FileForm
from files.models import File
from users.models import Teacher
from utils.constants import TAHSIN_STATUS_LIST
from utils_humas.mixins import GeneralAuthPermissionMixin, GeneralContextMixin, GeneralFormDeleteMixin, GeneralFormValidateMixin
from students.models import Student
from tahfidz.models import Tahfidz, Tilawah
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from tahfidz.forms import TahfidzForm, TilawahForm
from userlog.models import UserLog
from utils.whatsapp_albinaa import send_WA_create_update_delete
from numpy import int8


# Tahfidz Controllers
class TahfidzIndexView(GeneralContextMixin, ListView):
    model = Tahfidz

class TahfidzCreateView(GeneralFormValidateMixin, CreateView):
    model = Tahfidz
    form_class = TahfidzForm
    form_name = "Create"
    app_name = "Tahfidz"
    type_url = 'tahfidz/'
    permission_required = 'tahfidz.add_tahfidz'

class TahfidzQuickUploadView(GeneralAuthPermissionMixin, CreateView):
    model = File
    form_class = FileForm
    permission_required = 'tahfidz.add_tahfidz'
    template_name = 'tahfidz/tahfidz_form.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        df = read_excel(self.object.file, na_filter=False, dtype={"NIS": str})
        row, _ = df.shape
        for i in range(row):
            try:
                Tahfidz.objects.update_or_create(
                    santri = Student.objects.select_related.get(nis=df.iloc[i, 0]),
                    defaults=dict(
                        hafalan = df.iloc[i, 2],
                        pencapaian_sebelumnya = df.iloc[i, 3],
                        pencapaian_sekarang = df.iloc[i, 4],
                        catatan = df.iloc[i, 5],
                        pembimbing = df.iloc[i, 6],
                    )
                )
            except:
                messages.error(self.request, "Data pada Excel TIDAK SESUAI FORMAT! Mohon sesuaikan dengan format yang ada. Hubungi Administrator jika kesulitan.")
                return HttpResponseRedirect(reverse("tahfidz:tahfidz-quick-create"))
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="TAHFIDZ",
                message="berhasil impor file Excel data tahfidz santri"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'impor file Excel', 'data tahfidz santri', 'tahfidz/')
        messages.success(self.request, "Import Data Excel Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Import Excel"
        return c
    

class TahfidzQuickCSVUploadView(GeneralAuthPermissionMixin, CreateView):
    model = File
    form_class = FileForm
    permission_required = 'tahfidz.add_tahfidz'
    template_name = 'tahfidz/tahfidz_form.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        df = read_csv(self.object.file, na_filter=False, dtype={"NIS": str})
        row, _ = df.shape
        for i in range(row):
            try:
                Tahfidz.objects.update_or_create(
                    santri = Student.objects.select_related('student_class').get(nis=df.iloc[i, 0]),
                    defaults=dict(
                        hafalan = df.iloc[i, 2],
                        pencapaian_sebelumnya = df.iloc[i, 3],
                        pencapaian_sekarang = df.iloc[i, 4],
                        catatan = df.iloc[i, 5],
                        pembimbing = df.iloc[i, 6],
                    )
                )
            except:
                messages.error(self.request, "Data pada CSV TIDAK SESUAI FORMAT! Mohon sesuaikan dengan format yang ada. Hubungi Administrator jika kesulitan.")
                return HttpResponseRedirect(reverse("tahfidz:tahfidz-quick-create-csv"))
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="CREATE",
                app="STUDENT",
                message="berhasil impor file CSV data tahfidz santri"
            )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'impor file CSV', 'data tahfidz santri', 'tahfidz/')
        messages.success(self.request, "Import Data CSV Berhasil! :)")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["form_name"] = "Import CSV"
        return c
    

class TahfidzDetailView(GeneralAuthPermissionMixin, DetailView):
    model = Tahfidz
    permission_required = 'tahfidz.view_tahfidz'

class TahfidzUpdateView(GeneralFormValidateMixin, UpdateView):
    model = Tahfidz
    form_class = TahfidzForm
    form_name = "Update"
    app_name = "Tahfidz"
    type_url = 'tahfidz/'
    permission_required = 'tahfidz.change_tahfidz'

class TahfidzDeleteView(GeneralFormDeleteMixin):
    model = Tahfidz
    success_url = reverse_lazy("tahfidz:tahfidz-list")
    app_name = "Tahfidz"
    type_url = 'tahfidz/'
    permission_required = 'tahfidz.delete_tahfidz'



class TilawahIndexView(GeneralContextMixin, ListView):
    model = Tilawah
    queryset = Tilawah.objects.select_related("santri__student_class").prefetch_related("pendamping").filter(santri__student_status="Aktif")
    paginate_by = 426

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        class_id = request.GET.get("class_id")
        date = request.GET.get("date")
        student_name = request.GET.get("student_name")
        if class_id:
            try:
                class_id = int(class_id)
            except:
                raise BadRequest("Kelas tidak valid!")
            self.queryset = self.queryset.filter(santri__student_class_id=class_id)
        if date:
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except:
                raise BadRequest("Tanggal tidak valid!")
            self.queryset = self.queryset.filter(tanggal=date)
        else:
            self.queryset = self.queryset.filter(tanggal=timezone.now().date())
        if student_name:
            self.queryset = self.queryset.filter(santri__student_name__icontains=student_name)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        class_id = self.request.GET.get("class_id")
        date = self.request.GET.get("date")
        student_name = self.request.GET.get("student_name")
        c["student_above_target"] = self.queryset.filter(santri__student_status="Aktif", tercapai=True).count()
        c["student_below_target"] = self.queryset.filter(santri__student_status="Aktif", tercapai=False).count()
        c["every_class_target"] = self.queryset.filter(santri__student_status="Aktif", tercapai=True).values("santri__student_class__short_class_name").annotate(total=Count("tercapai")).order_by("santri__student_class__short_class_name").distinct()
        c["every_class_target_false"] = self.queryset.filter(santri__student_status="Aktif", tercapai=False).values("santri__student_class__short_class_name").annotate(total=Count("tercapai")).order_by("santri__student_class__short_class_name").distinct()
        c["classes"] = Class.objects.filter(category="Putra")
        if class_id:
            c["class_id"] = int(class_id)
        if date:
            c["date"] = date
        if student_name:
            c["student_name"] = student_name
        return c
    

class QuickFillUnsubmittedTilawahView(GeneralContextMixin, ListView):
    model = Tilawah
    queryset = Tilawah.objects.select_related("santri__student_class").prefetch_related("pendamping").filter(santri__student_status="Aktif")
    paginate_by = 426

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        classes = Class.objects.filter(category="Putra")
        date = request.GET.get("date")
        if date:
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except:
                raise BadRequest("Tanggal tidak valid!")
        else:
            date = timezone.now().date()
        for class_ in classes:
            students = Student.objects.select_related("student_class").filter(student_status="Aktif", student_class=class_)
            for student in students:
                object, is_created = Tilawah.objects.get_or_create(
                    tanggal = date,
                    santri = student,
                    defaults=dict(
                        tercapai = False,
                        halaman = 0,
                        target = 1,
                        catatan = "",
                        tajwid = None,
                        kelancaran = None,
                    )
                )
        
        return HttpResponseRedirect(reverse("tahfidz:tilawah-list"))


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["date"] = self.request.GET.get("date")
        if c["date"]:
            try:
                c["date"] = datetime.strptime(c["date"], "%Y-%m-%d").date()
            except:
                raise BadRequest("Tanggal tidak valid!")
        return c
    

class TilawahCreateView(GeneralFormValidateMixin, CreateView):
    model = Tilawah
    form_class = TilawahForm
    form_name = "Create"
    app_name = "Tilawah"
    type_url = 'tahfidz/tilawah/'
    permission_required = 'tahfidz.add_tilawah'

class TilawahQuickUploadView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Tilawah
    form_class = TilawahForm
    template_name = 'tahfidz/tilawah_create.html'
    permission_required = 'tahfidz.add_tilawah'
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        class_id = request.POST.get("class_id")
        date = request.POST.get("date")
        target = request.POST.get("target")
        catatan = request.POST.get("catatan")
        if not date or not class_id or not target:
            return HttpResponseBadRequest("Tanggal atau Kelas atau Target tidak boleh kosong!")
        teachers = request.POST.getlist("teachers")
        students = Student.objects.select_related("student_class").filter(student_status="Aktif", student_class_id=class_id)
        for student in students:
            nis_santri = request.POST.get(f"student{student.nis}")
            tajwid = request.POST.get(f"tajwid{student.nis}")
            kelancaran = request.POST.get(f"kelancaran{student.nis}")
            halaman = request.POST.get(f"halaman{student.nis}", 0)
            if nis_santri:
                object, is_updated = Tilawah.objects.select_related("santri").prefetch_related("pendamping").update_or_create(
                    tanggal = date,
                    santri = student,
                    defaults=dict(
                        tercapai = True if target and int(halaman) >= int(target) else False,
                        halaman = halaman,
                        target = target,
                        catatan = catatan,
                        tajwid = tajwid if tajwid != "null" and tajwid in TAHSIN_STATUS_LIST else None,
                        kelancaran = kelancaran if kelancaran != "null" and kelancaran in TAHSIN_STATUS_LIST else None,
                    )
                )
                if teachers:
                    teachers_list = [Teacher.objects.get(id=teacher_id) for teacher_id in teachers]
                    object.pendamping.set(teachers_list)
                object.save()

        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="CREATE",
            app="TILAWAH",
            message=f"berhasil menambahkan banyak data tilawah"
        )
        messages.success(self.request, "Input tilawah berhasil!")
        return redirect(reverse("tahfidz:tilawah-list"))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["classes"] = Class.objects.filter(category="Putra")
        context["teachers"] = Teacher.objects.filter(status="Aktif", gender="L")
        if settings.DEBUG:
            context["debug"] = "debug"
        else:
            context["debug"] = "prod"

        return context
    

class TilawahDetailView(GeneralAuthPermissionMixin, DetailView):
    model = Tilawah
    permission_required = 'tahfidz.view_tilawah'

class TilawahUpdateView(GeneralFormValidateMixin, UpdateView):
    model = Tilawah
    form_class = TilawahForm
    form_name = "Update"
    app_name = "Tilawah"
    type_url = 'tahfidz/tilawah/'
    permission_required = 'tahfidz.change_tilawah'

class TilawahDeleteView(GeneralFormDeleteMixin):
    model = Tilawah
    success_url = reverse_lazy("tahfidz:tahfidz-list")
    app_name = "Tilawah"
    type_url = 'tahfidz/tilawah/'
    permission_required = 'tahfidz.delete_tilawah'