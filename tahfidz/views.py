from datetime import datetime
from django.db.models.query import QuerySet
from django.utils import timezone
from django.db.models import Count, Case, When, IntegerField, Sum, Subquery, OuterRef
from typing import Any
from django.conf import settings
from django.core.exceptions import PermissionDenied, BadRequest
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from pandas import read_csv, read_excel
from classes.models import Class
from files.forms import FileForm
from files.models import File
from users.models import Teacher
from utils.constants import QURAN_SURAH_DICT, TAHSIN_STATUS_LIST
from utils.mixins import GeneralDownloadExcelView
from utils.surat_quran import QURAN_SURAH
from utils_humas.mixins import GeneralAuthPermissionMixin, GeneralContextMixin, GeneralFormDeleteMixin, GeneralFormValidateMixin
from students.models import Student
from tahfidz.models import Tahfidz, Target, Tilawah
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from tahfidz.forms import TahfidzForm, TargetForm, TilawahForm
from userlog.models import UserLog
from utils.whatsapp_albinaa import send_WA_create_update_delete
from numpy import int8

from utils_piket.mixins import ModelDownloadExcelView


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
        target_tilawah = get_object_or_404(Target, tanggal=date)
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
                        target_tilawah = target_tilawah,
                        surat = 1,
                        ayat = 0,
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
        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except:
            raise BadRequest("Tanggal tidak valid!")
        teachers = request.POST.getlist("teachers")
        students = Student.objects.select_related("student_class").filter(student_status="Aktif", student_class_id=class_id)
        target_tilawah = get_object_or_404(Target, tanggal=date)
        for student in students:
            nis_santri = request.POST.get(f"student{student.nis}")
            tajwid = request.POST.get(f"tajwid{student.nis}")
            kelancaran = request.POST.get(f"kelancaran{student.nis}")
            halaman = request.POST.get(f"halaman{student.nis}", 0)
            kehadiran = request.POST.get(f"kehadiran{student.nis}", "Hadir")
            ayat = request.POST.get(f"ayat{student.nis}", 0)
            surat = request.POST.get(f"surat{student.nis}", 1)
            if nis_santri:
                object, is_updated = Tilawah.objects.select_related("santri").prefetch_related("pendamping").update_or_create(
                    tanggal = date,
                    santri = student,
                    defaults=dict(
                        tercapai = True if target and int(halaman) >= int(target) and int(surat) >= int(target_tilawah.nomor_surat) and int(ayat) >= int(target_tilawah.ayat) else False,
                        halaman = halaman,
                        target = target,
                        ayat = ayat if ayat else None,
                        surat = surat if surat else None,
                        kehadiran = kehadiran,
                        target_tilawah = target_tilawah,
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

class TargetListView(ListView):
    model = Target

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        date_query = request.GET.get("date_query")
        query = request.GET.get("query")
        if date_query:
            try:
                date_query = datetime.strptime(date_query, "%Y-%m-%d").date()
            except:
                raise BadRequest("Tanggal tidak valid!")
            data = list(Target.objects.filter(tanggal=date_query).values("tanggal", "nomor_surat", "nama_surat", "ayat"))
            return JsonResponse(data, safe=False)
        elif query == "surah":
            surah = list({id: name} for (id, name) in QURAN_SURAH)
            return JsonResponse(surah, safe=False)
        return super().get(request, *args, **kwargs)
    
class TargetQuickUploadView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Target
    form_class = FileForm
    template_name = 'components/form.html'
    permission_required = 'tahfidz.add_target'
    form_name = "Tahfidz"
    form_link = "Tahfidz:Tilawah"


    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save(commit=False)
        df = read_excel(self.object.file, na_filter=False)
        row, _ = df.shape
        try:
            for i in range(row):
                if df.iloc[i, 1]:
                    Target.objects.update_or_create(
                        tanggal = df.iloc[i, 1],
                        defaults=dict(
                            nomor_surat = df.iloc[i, 2],
                            nama_surat = df.iloc[i, 3],
                            ayat = df.iloc[i, 4],
                        )
                    )
        except Exception as e:
            messages.error(self.request, f"Error: {e}.")
            return HttpResponseRedirect(reverse("tahfidz:target-upload"))

        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="CREATE",
            app="TARGET",
            message=f"berhasil menambahkan banyak data target tilawah"
        )
        messages.success(self.request, "Input target tilawah berhasil!")
        return redirect(reverse("tahfidz:tilawah-list"))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form_name"] = self.form_name
        context["form_link"] = self.form_link

        return context
    

class TilawahDetailView(GeneralAuthPermissionMixin, DetailView):
    model = Student
    permission_required = 'tahfidz.view_tilawah'
    template_name = 'tahfidz/tilawah_detail.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["history"] = Tilawah.objects.filter(santri=self.object).order_by("-tanggal")
        obj = self.get_object()
        c["student_id"] = obj.id
        return c


class TilawahClassReportView(GeneralContextMixin, ListView):
    model = Tilawah
    queryset = Tilawah.objects.select_related("santri__student_class").prefetch_related("pendamping").filter(santri__student_status="Aktif")
    paginate_by = 426
    template_name = "tahfidz/tilawah_detail.html"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        class_id = self.request.GET.get("class_id")
        if not class_id:
            raise BadRequest("Kelas harus dipilih!")
        try:
            class_id = int(class_id)
        except:
            raise BadRequest("Kelas tidak valid!")
        students = Student.objects.filter(student_class=class_id, student_status="Aktif")  # adjust class filter

        latest_tilawah = Tilawah.objects.filter(santri=OuterRef('pk')).order_by('-tanggal')

        recap = students.annotate(
            hadir_count=Count(Case(When(tilawah__kehadiran="Hadir", then=1), output_field=IntegerField())),
            sakit_count=Count(Case(When(tilawah__kehadiran="Sakit", then=1), output_field=IntegerField())),
            telat_count=Count(Case(When(tilawah__kehadiran="Telat", then=1), output_field=IntegerField())),
            izin_count=Count(Case(When(tilawah__kehadiran="Izin", then=1), output_field=IntegerField())),
            alpa_count=Count(Case(When(tilawah__kehadiran="Alpa", then=1), output_field=IntegerField())),

            # Get latest tajwid and kelancaran from Tilawah
            latest_surat=Subquery(latest_tilawah.values('surat')[:1]),
            latest_ayat=Subquery(latest_tilawah.values('ayat')[:1]),
            latest_halaman=Subquery(latest_tilawah.values('halaman')[:1]),
            latest_tercapai=Subquery(latest_tilawah.values('tercapai')[:1]),
            latest_tajwid=Subquery(latest_tilawah.values('tajwid')[:1]),
            latest_kelancaran=Subquery(latest_tilawah.values('kelancaran')[:1]),
        ).values(
            'student_name',
            'hadir_count',
            'sakit_count',
            'telat_count',
            'izin_count',
            'alpa_count',
            'latest_surat',
            'latest_ayat',
            'latest_halaman',
            'latest_tercapai',
            'latest_tajwid',
            'latest_kelancaran'
        )
        c["recap"] = recap
        c["date"] = timezone.now().date()
        c["class"] = get_object_or_404(Class, pk=class_id)
        c["type"] = "class_report"
        c["class_id"] = class_id
        return c


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


class TilawahDownloadExcelView(ModelDownloadExcelView):
    app_name = 'Tilawah'
    menu_name = 'Tilawah'
    permission_required = 'tahfidz.view_tilawah'
    template_name = 'alumni/download.html'
    header_names = ['No', 'NIS', 'Nama', 'Kelas', 'Tercapai', 'Target Halaman', 'Halaman', 'Surat', 'Ayat', 'Tajwid', "Kelancaran", "Keterangan"]
    filename = 'Data Tilawah SMA IT Al Binaa.xlsx'
    queryset = Tilawah.objects.select_related("santri", "target_tilawah").prefetch_related("pendamping").all()

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        class_id = request.GET.get("class_id")
        student_id = request.GET.get("student_id")
        if class_id:
            self.queryset = self.queryset.filter(santri__student_class_id=class_id)
        elif student_id:
            self.queryset = self.queryset.filter(santri__id=student_id)
        return super().get(request, *args, **kwargs)