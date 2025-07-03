from typing import Any
from django.db.models import Count, QuerySet, Q
from django.views.generic import ListView
from django.utils import timezone
import requests
from alumni.models import Alumni
from extracurriculars.models import Extracurricular
from private.models import Private, Subject
from students.models import Student
from laporan.models import Report
from prestasi.models import Prestasi
from userlog.models import UserLog

# Create your views here.
class HomeView(ListView):
    model = Prestasi
    template_name = 'index.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Prestasi.objects.exclude(Q(photo='no-image.png') | Q(photo__isnull=True))[:12]
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['ekskul'] = Extracurricular.objects.prefetch_related('teacher').filter(status="Aktif").order_by('type', 'name')
        context['kegiatan'] = Report.objects.exclude(photo='no-image.png').select_related('extracurricular')[:12]
        return context
    
    
class Dashboard(ListView):
    model = Extracurricular
    template_name = 'dashboard/dashboard.html'
    queryset = Extracurricular.objects.filter(status="Aktif")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        extracurriculars_and_study_groups = list(self.queryset)
        context["extracurricular"] = [item for item in extracurriculars_and_study_groups if item.type == "Ekskul"]
        context["study_club"] = [item for item in extracurriculars_and_study_groups if item.type == "SC"]
        context["students"] = Student.objects.select_related('student_class').filter(student_status="Aktif")
        context["active_students"] = Student.objects.select_related('student_class').filter(student_status="Aktif", pk__in=Extracurricular.objects.select_related('members').values_list('members', flat=True).filter(members__isnull=False, status="Aktif").distinct())
        context["inactive_students"] = Student.objects.select_related('student_class').filter(student_status="Aktif").exclude(id__in=context["active_students"]).order_by("student_class__class_name", "student_name")
        context["inactive_students_x"] = Student.objects.select_related('student_class').filter(student_status="Aktif", student_class__class_name__startswith="X-").exclude(id__in=context["active_students"]).order_by("student_class__class_name", "student_name")
        context["inactive_students_xi"] = Student.objects.select_related('student_class').filter(student_status="Aktif", student_class__class_name__startswith="XI-").exclude(id__in=context["active_students"]).order_by("student_class__class_name", "student_name")
        context["inactive_students_xii"] = Student.objects.select_related('student_class').filter(student_status="Aktif", student_class__class_name__startswith="XII-").exclude(id__in=context["active_students"]).order_by("student_class__class_name", "student_name")
        context["active_extracurricular"] = Report.objects.select_related('extracurricular', 'teacher').values_list('extracurricular', flat=True).distinct()
        context["inactive_extracurricular"] = Extracurricular.objects.exclude(id__in=context["active_extracurricular"]).filter(status="Aktif")
        context["report"] = Report.objects.filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).select_related('extracurricular', 'teacher').values('report_date').annotate(dcount=Count('report_date')).distinct().order_by('-report_date')[:11]
        context["report_extracurricular"] = Report.objects.select_related('extracurricular', 'teacher').filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).values('extracurricular__name').annotate(count=Count('extracurricular')).order_by().distinct()
        context["logs"] = UserLog.objects.all()[:10]
        return context

class InactiveReportView(ListView):
    model = Report
    template_name = "extracurriculars/extracurricular_inactive_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        active = Report.objects.filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).select_related('extracurricular').values_list('extracurricular', flat=True).distinct()
        data = Extracurricular.objects.filter(status="Aktif").exclude(id__in=active)
        return data

    

class HumasDashboardView(ListView):
    model = Alumni
    template_name = 'dashboard.html'
    queryset = Alumni.objects.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        
        c["jumlah_santri"] = Student.objects.select_related('student_class').filter(status="Aktif")
        c["jumlah_santri_putra"] = c["jumlah_santri"].filter(status="Aktif", jenis_kelamin="L").count()
        c["jumlah_santri_putri"] = c["jumlah_santri"].filter(status="Aktif", jenis_kelamin="P").count()
        c["jumlah_private"] = Private.objects.all()
        c["jumlah_private_bulan_ini"] = c["jumlah_private"].filter(tanggal_bimbingan__month=timezone.now().month).count()
        c["jumlah_private_bulan_lalu"] = c["jumlah_private"].filter(tanggal_bimbingan__month=timezone.now().month-1).count()
        c["jumlah_mapel_private"] = Subject.objects.select_related("pelajaran").all()
        c["jumlah_mapel_private_aktif"] = c["jumlah_private"].values_list("pelajaran").distinct()
        c["jumlah_mapel_private_nonaktif"] = Subject.objects.exclude(pk__in=c["jumlah_mapel_private_aktif"]).count()
        c["jumlah_alumni_putra"] = self.queryset.filter(gender="L")
        c["jumlah_alumni_putri"] = self.queryset.filter(gender="P")
        c["jumlah_alumni_tahun_ini"] = self.queryset.filter(graduate_year=timezone.now().year)
        c["jumlah_alumni_putra_tahun_ini"] = self.queryset.filter(gender="L", graduate_year=timezone.now().year)
        c["jumlah_alumni_putri_tahun_ini"] = self.queryset.filter(gender="P", graduate_year=timezone.now().year)
        c["jumlah_alumni_universitas"] = self.queryset.exclude(undergraduate_university__isnull=True)
        c["jumlah_alumni_putra_universitas"] = self.queryset.filter(gender="L").exclude(undergraduate_university__isnull=True)
        c["jumlah_alumni_putra_non_univ"] = self.queryset.filter(gender="L", undergraduate_university="")
        c["jumlah_alumni_putri_universitas"] = self.queryset.filter(gender="P").exclude(undergraduate_university__isnull=True)
        c["jumlah_alumni_putri_non_univ"] = self.queryset.filter(gender="P", undergraduate_university="")
        c["logs"] = UserLog.objects.order_by("-created_at")[:10]
        c["sebaran_universitas_sarjana"] = self.queryset.exclude(undergraduate_university__in=[0, '']).values('undergraduate_university')\
                                                        .annotate(dcount=Count('undergraduate_university')).order_by('-dcount')[:20]

        return c