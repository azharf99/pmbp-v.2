import os
from typing import Any
from django.conf import settings
from django.contrib import messages
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from pandas import read_excel
from files.forms import FileForm
from files.models import File
from utils_humas.mixins import GeneralAuthPermissionMixin, GeneralContextMixin, GeneralFormDeleteMixin, GeneralFormValidateMixin
from private.models import Private, Subject, Group
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from private.forms import PrivateCreateForm, PrivateUpdateForm, SubjectForm, GroupForm
from students.models import Student
from userlog.models import UserLog
from utils.whatsapp_albinaa import send_WA_create_update_delete
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Count


# Private Controllers
class PrivateIndexView(GeneralContextMixin, ListView):
    model = Private
    paginate_by = 51

    def get_queryset(self) -> QuerySet[Any]:
        month = self.request.GET.get("month")
        year = self.request.GET.get("year")
        if month and year:
            return Private.objects.prefetch_related("kehadiran_santri", "kelompok__santri", "pembimbing", "pelajaran__pembimbing", "kelompok__pelajaran")\
                                .filter(tanggal_bimbingan__month=month, tanggal_bimbingan__year=year)
        return super().get_queryset().prefetch_related("kehadiran_santri", "kelompok__santri", "pembimbing", "pelajaran", "kelompok__pelajaran")


class PrivateCreateView(GeneralFormValidateMixin, CreateView):
    model = Private
    form_class = PrivateCreateForm
    success_message = "Input laporan privat berhasil!"
    form_name = "Create"
    app_name = "Private"
    type_url = 'private/'
    permission_required = 'private.add_private'

    def get_form_kwargs(self) -> dict[str, Any]:
        k = super().get_form_kwargs()
        k["user"] = self.request.user
        k["subject"] = Subject.objects.prefetch_related("pembimbing").all()
        return k

class PrivateDetailView(GeneralAuthPermissionMixin, DetailView):
    model = Private
    permission_required = 'private.view_private'


class PrivateUpdateView(GeneralFormValidateMixin, UpdateView):
    model = Private
    form_class = PrivateUpdateForm
    success_message = "Update laporan privat berhasil!"
    form_name = "Update"
    app_name = "Private"
    type_url = 'private/'
    permission_required = 'private.delete_private'

    def get_form_kwargs(self) -> dict[str, Any]:
        k = super().get_form_kwargs()
        k["user"] = self.request.user
        k["subject"] = Subject.objects.prefetch_related("pembimbing").all()
        return k

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.get_object().pembimbing == request.user.teacher or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

class PrivateDeleteView(GeneralFormDeleteMixin):
    model = Private
    success_url = reverse_lazy("private:private-index")
    app_name = 'Private'
    type_url = 'private/'
    permission_required = 'private.delete_private'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.get_object().pembimbing == request.user.teacher or request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied


# Subject Controllers
class SubjectIndexView(GeneralContextMixin ,ListView):
    model = Subject

class SubjectCreateView(GeneralAuthPermissionMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    form_name = "Create"
    app_name = "Subject"
    type_url = 'private/'
    slug_url = 'subjects/'
    permission_required = 'subject.add_subject'

class SubjectDetailView(GeneralAuthPermissionMixin, DetailView):
    model = Subject
    permission_required = 'subject.view_subject'

class SubjectUpdateView(GeneralFormValidateMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    form_name = "Update"
    app_name = "Subject"
    type_url = 'private/'
    slug_url = 'subjects/'
    permission_required = 'subject.change_subject'
    

class SubjectDeleteView(GeneralFormDeleteMixin):
    model = Subject
    success_url = reverse_lazy("private:subject-index")
    app_name = "Subject"
    type_url = 'private/'
    slug_url = 'subjects/'
    permission_required = 'subject.delete_subject'

# Group Controllers
class GroupIndexView(GeneralContextMixin ,ListView):
    model = Group

class GroupCreateView(GeneralAuthPermissionMixin, CreateView):
    model = Group
    form_class = GroupForm
    form_name = "Create"
    app_name = "Group"
    type_url = 'private/'
    slug_url = 'groups/'
    permission_required = 'group.add_group'


class GroupQuickUploadView(GeneralAuthPermissionMixin, CreateView):
    model = File
    form_class = FileForm
    form_name = "Import Excel Kelompok Privat"
    permission_required = 'alumni.add_files'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        df = read_excel(self.object.file, na_filter=False, dtype={"NIS": str})
        row, _ = df.shape
        try:
            for i in range(row):
                obj, created = Group.objects.update_or_create(
                    nama_kelompok = df.iloc[i, 0],
                    jenis_kelompok = df.iloc[i, 1],
                    pelajaran = Subject.objects.get(pk=df.iloc[i, 2]),
                    defaults=dict(
                        jadwal = df.iloc[i, 3],
                        waktu = df.iloc[i, 4]
                    )
                )
                obj.santri.add(Student.objects.get(nis=df.iloc[i, 5]))
                obj.save()
        except:
            messages.error(self.request, "Data pada Excel TIDAK SESUAI FORMAT! Mohon sesuaikan dengan format yang ada. Hubungi Administrator jika kesulitan.")
            return HttpResponseRedirect(reverse("private:group-index"))
        UserLog.objects.create(
            user = self.request.user.teacher,
            action_flag = "CREATE",
            app = "GROUP",
            message = f"berhasil impor data excel kelompok privat"
        )
        messages.success(self.request, "Selamat, Impor data excel kelompok privat berhasil!")
        send_WA_create_update_delete(self.request.user.teacher.no_hp, 'mengimpor dari excel', 'data kelompok privat', 'private/', 'groups/')
        return HttpResponseRedirect(self.get_success_url())



class GroupDetailView(GeneralAuthPermissionMixin, DetailView):
    model = Group
    permission_required = 'group.view_group'

class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    form_name = "Update"
    app_name = "Group"
    type_url = 'private/'
    slug_url = 'groups/'
    permission_required = 'group.change_group'


class GroupDeleteView(GeneralFormDeleteMixin):
    model = Group
    app_name = "Group"
    type_url = 'private/'
    slug_url = 'groups/'
    permission_required = 'group.delete_group'
    success_url = reverse_lazy("private:group-index")


class GroupGetView(LoginRequiredMixin, DetailView):
    model = Group

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        query = request.GET.get("query")
        if query:
            data = list(Group.objects.filter(pk=query).values("santri", "santri__nama_siswa", "santri__kelas__nama_kelas"))
            extra_data = list(Student.objects.select_related("student_class").filter(kelas__nama_kelas__startswith="XII").exclude(pk__in=Group.objects.filter(pk=query).values_list("santri")).values("id", "nama_siswa", "kelas__nama_kelas"))
            full_data = dict()
            full_data["utama"] = data
            full_data["ekstra"] = extra_data
            return JsonResponse(full_data, safe=False)
        else:
            data = {
                "utama": [
                    {
                    "santri": None,
                    "santri__nama_siswa": "Error! Harus Pilih Kelompok!"
                    },
                    {
                    "santri": None,
                    "santri__nama_siswa": "Jika Bingung, Hubungi Admin!"
                    }
                ]
            }

        return JsonResponse(data, safe=False)


class PrivateOptionsView(ListView):
    model = Private
    template_name = 'private/private_options.html'
    queryset = Private.objects.prefetch_related("kehadiran_santri", "kelompok__santri", "pembimbing", "pelajaran__pembimbing", "kelompok__pelajaran").values("tanggal_bimbingan__month", "tanggal_bimbingan__year").order_by().distinct()
    
    def get_queryset(self) -> QuerySet[Any]:
        month_names = {
            1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
            5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
            9: "September", 10: "Oktober", 11: "November", 12: "Desember"
        }

        monthList = list()
        monthSet = set()
        yearSet = set()
        allDict = dict()
        for i in self.queryset:
                monthSet.add(i['tanggal_bimbingan__month'])
                yearSet.add(i['tanggal_bimbingan__year'])
        for i in monthSet:
            monthList.append({"nama": month_names.get(i), "value": i})
        allDict["month"] = monthList
        allDict["year"] = list(yearSet)
        return [allDict]


class PrivatePrintView(LoginRequiredMixin, ListView):
    model = Private
    template_name = 'private/private_print.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self) -> QuerySet[Any]:
        month = self.request.GET.get("month")
        year = self.request.GET.get("year")
        if month and year:
            return Private.objects.prefetch_related("kehadiran_santri", "kelompok__santri", "pembimbing", "pelajaran__pembimbing", "kelompok__pelajaran").filter(tanggal_bimbingan__month=month, tanggal_bimbingan__year=year).values("pembimbing__nama_guru").annotate(dcount=Count("pelajaran"))
        return Private.objects.prefetch_related("kehadiran_santri", "kelompok__santri", "pembimbing", "pelajaran__pembimbing", "kelompok__pelajaran").filter(tanggal_bimbingan__month=timezone.now().month, tanggal_bimbingan__year=timezone.now().year).values("pembimbing__nama_guru").annotate(dcount=Count("pelajaran"))
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        MONTHS = {
            1: "Januari",
            2: "Februari",
            3: "Maret",
            4: "April",
            5: "Mei",
            6: "Juni",
            7: "Juli",
            8: "Agustus",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember",
        }
        c["tahun_ajaran"] = settings.TAHUN_AJARAN
        month = self.request.GET.get("month")
        year = self.request.GET.get("year")

        if month and year:
            c["bulan_privat"] = MONTHS.get(int(month))
            c["jumlah_privat"] = Private.objects.prefetch_related("kehadiran_santri", "kelompok__santri", "pembimbing", "pelajaran__pembimbing", "kelompok__pelajaran").filter(tanggal_bimbingan__month=month, tanggal_bimbingan__year=year).all()
            c["site_title"] = f"Rekap Privat {c['bulan_privat']} {year}"
        else:
            c["bulan_privat"] = MONTHS.get(timezone.now().month)
            c["site_title"] = f"Rekap Privat {c['bulan_privat']} {timezone.now().year}"
            c["jumlah_privat"] = Private.objects.prefetch_related("kehadiran_santri", "kelompok__santri", "pembimbing", "pelajaran__pembimbing", "kelompok__pelajaran").filter(tanggal_bimbingan__month=timezone.now().month, tanggal_bimbingan__year=timezone.now().year).all()
        return c
    