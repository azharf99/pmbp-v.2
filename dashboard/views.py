from typing import Any
from django.db.models import Count, QuerySet, Q
from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView
from django.utils import timezone
from alumni.models import Alumni
from classes.models import Class
from courses.models import Course
from extracurriculars.models import Extracurricular
from notifications.models import Notification
from private.models import Private, Subject
from students.models import Student
from laporan.models import Report
from prestasi.models import Prestasi
from userlog.models import UserLog
from users.models import Teacher

# Create your views here.
class HomeView(ListView):
    model = Prestasi
    template_name = 'pmbp.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Prestasi.objects.exclude(Q(photo='no-image.png') | Q(photo__isnull=True))[:12]
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['ekskul'] = Extracurricular.objects.prefetch_related('teacher').filter(status="Aktif").order_by('type', 'name')
        context['kegiatan'] = Report.objects.exclude(photo='no-image.png').select_related('extracurricular')[:12]
        return context
    
    
class DashboardView(ListView):
    model = Extracurricular
    template_name = 'dashboard.html'
    queryset = Extracurricular.objects.filter(status="Aktif")

    
    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        response = super().render_to_response(context, **response_kwargs)
        
        reports = list(Report.objects.filter(report_date__year=timezone.now().year).select_related('extracurricular', 'teacher').values('report_date').annotate(dcount=Count('report_date')).distinct().order_by('-report_date')[:11])
        extracurricular_reports = list(Report.objects.select_related('extracurricular', 'teacher').filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).values('extracurricular__name').annotate(count=Count('extracurricular')).order_by().distinct())
        jumlah_alumni_universitas = list(Alumni.objects.exclude(undergraduate_university__in=[0, '', None]).values('undergraduate_university').annotate(count=Count('undergraduate_university')).order_by("-count").distinct())


        reports_keys = ":".join([str(data["report_date"]) for data in reports])
        reports_values = ":".join([str(data["dcount"]) for data in reports])
        extracurricular_reports_keys = ":".join([str(data["extracurricular__name"]) for data in extracurricular_reports])
        extracurricular_reports_values = ":".join([str(data["count"]) for data in extracurricular_reports])
        alumni_keys = ":".join([str(data["undergraduate_university"]) for data in jumlah_alumni_universitas[:10]])
        alumni_values = ":".join([str(data["count"]) for data in jumlah_alumni_universitas[:10]])


        response.set_cookie('reports_keys', reports_keys) 
        response.set_cookie('reports_values', reports_values) 
        response.set_cookie('extracurricular_reports_keys', extracurricular_reports_keys) 
        response.set_cookie('extracurricular_reports_values', extracurricular_reports_values) 
        response.set_cookie('alumni_keys', alumni_keys) 
        response.set_cookie('alumni_values', alumni_values) 
        return response

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        extracurriculars_and_study_groups = list(self.queryset)
        # context["extracurricular"] = [item for item in extracurriculars_and_study_groups if item.type == "Ekskul"]
        # context["study_club"] = [item for item in extracurriculars_and_study_groups if item.type == "SC"]
        context["students"] = Student.objects.select_related('student_class').filter(student_status="Aktif")
        context["teachers"] = Teacher.objects.select_related('user').exclude(id__in=["31", "112", "110", "35", "113", "111"]).filter(status="Aktif", gender="L")
        context["classes"] = Class.objects.filter(category="Putra")
        context["userlogs"] = UserLog.objects.all()[:7]
        context["extracurriculars_and_study_groups"] = extracurriculars_and_study_groups
        # context["active_students"] = Student.objects.select_related('student_class').filter(student_status="Aktif", pk__in=Extracurricular.objects.select_related('members').values_list('members', flat=True).filter(members__isnull=False, status="Aktif").distinct())
        # context["inactive_students"] = Student.objects.select_related('student_class').filter(student_status="Aktif").exclude(id__in=context["active_students"]).order_by("student_class__class_name", "student_name")
        # context["inactive_students_x"] = Student.objects.select_related('student_class').filter(student_status="Aktif", student_class__class_name__startswith="X-").exclude(id__in=context["active_students"]).order_by("student_class__class_name", "student_name")
        # context["inactive_students_xi"] = Student.objects.select_related('student_class').filter(student_status="Aktif", student_class__class_name__startswith="XI-").exclude(id__in=context["active_students"]).order_by("student_class__class_name", "student_name")
        # context["inactive_students_xii"] = Student.objects.select_related('student_class').filter(student_status="Aktif", student_class__class_name__startswith="XII-").exclude(id__in=context["active_students"]).order_by("student_class__class_name", "student_name")
        # context["active_extracurricular"] = Report.objects.select_related('extracurricular', 'teacher').values_list('extracurricular', flat=True).distinct()
        # context["inactive_extracurricular"] = Extracurricular.objects.exclude(id__in=context["active_extracurricular"]).filter(status="Aktif")
        # context["report"] = Report.objects.filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).select_related('extracurricular', 'teacher').values('report_date').annotate(dcount=Count('report_date')).distinct().order_by('-report_date')[:11]
        context["report_extracurricular_length"] = len(Report.objects.select_related('extracurricular', 'teacher').filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).values('extracurricular__name').annotate(count=Count('extracurricular')).order_by().distinct())
        context["logs"] = UserLog.objects.all()[:10]
        context["jumlah_private"] = list(Private.objects.all())
        context["jumlah_private_bulan_ini"] = [private for private in context["jumlah_private"] if private.tanggal_bimbingan.month==timezone.now().month]
        # context["jumlah_private_bulan_lalu"] = context["jumlah_private"].filter(tanggal_bimbingan__month=timezone.now().month-1).count()
        context["jumlah_mapel_private"] = Subject.objects.select_related("pelajaran").all()
        # context["jumlah_mapel_private_aktif"] = context["jumlah_private"].values_list("pelajaran").distinct()
        # context["jumlah_mapel_private_nonaktif"] = Subject.objects.exclude(pk__in=context["jumlah_mapel_private_aktif"]).count()
        context["jumlah_alumni"] = list(Alumni.objects.all())
        context["jumlah_alumni_putra"] = [alumnus for alumnus in context["jumlah_alumni"] if alumnus.gender=="L"]
        context["jumlah_alumni_putri"] = [alumnus for alumnus in context["jumlah_alumni"] if alumnus.gender=="P"]
        
        context["jumlah_alumni_universitas"] = Alumni.objects.exclude(undergraduate_university__in=[0, ''])
        context["jumlah_alumni_non_univ"] = Alumni.objects.filter(undergraduate_university__in=[0, ''])
        context["logs"] = UserLog.objects.order_by("-created_at")[:10]
        # Courses
        context["sum_of_course"] = list(Course.objects.select_related("teacher").exclude(course_code__in=["APE", "LQ1", "TKL", "APEN3"]).filter(type="putra").values("course_name", "category").distinct())
        context["sum_of_course_syari"] = [subject for subject in context["sum_of_course"] if subject["category"]=="Syar'i"]
        context["sum_of_course_ashri"] = [subject for subject in context["sum_of_course"] if subject["category"]=="Ashri"]

        context["notifications"] = list(Notification.objects.filter(teacher=self.request.user.teacher))
        context["notifications_left"] = [notif for notif in context["notifications"] if notif.is_read==False]
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