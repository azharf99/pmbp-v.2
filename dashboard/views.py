from typing import Any
from django.db.models import Count, QuerySet, Q
from django.views.generic import ListView
from django.utils import timezone
import requests
from extracurriculars.models import Extracurricular
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
        context['ekskul'] = Extracurricular.objects.prefetch_related('teacher').order_by('type', 'name')
        context['kegiatan'] = Report.objects.exclude(photo='no-image.png').select_related('extracurricular')[:12]
        return context
    
    
class Dashboard(ListView):
    model = Extracurricular
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        level = self.request.GET.get("level", "")
        year = self.request.GET.get("year", "")
        
        url = "https://simt.kemdikbud.go.id/api/get-count-prestasi-cluster?npsn=20253130"
        url_sebaran = "https://simt.kemdikbud.go.id/api/get-count-pesebaran-sekolah?page=1&per_page=60&npsn=20253130"
        url_siswa = f"https://simt.kemdikbud.go.id/api/list-prestasi-siswa-per-sekolah?page=1&per_page=60&tingkat_prestasi={level}&npsn=20253130&tahun={year}"
    
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://simt.kemdikbud.go.id/"
        }

        try:
            response = requests.get(url, headers=headers)
            response_sebaran = requests.get(url_sebaran, headers=headers)
            response_siswa = requests.get(url_siswa, headers=headers)
            res = response.json()
            res_sebaran = response_sebaran.json()
            res_siswa = response_siswa.json()
        except:
            res = {"result": {"list": []}}
            res_sebaran = {"result": {"header": ["No.", "Tingkat Pendidikan", "2020", "2021", "2022", "2023", "2024", "Total"], "data": [
                "1",
                "SMAS IT AL BINAA",
                "1",
                "5",
                "10",
                "16",
                "15",
                "47"
            ]}}
            res_siswa = {"result": {"list": [], "pagination": {"total_page":0}}}
        
        context = super().get_context_data(**kwargs)
        context["extracurricular"] = self.get_queryset().filter(type="Ekskul")
        context["study_club"] = self.get_queryset().filter(type="SC")
        context["students"] = Student.objects.filter(student_status="Aktif")
        context["active_students"] = Student.objects.filter(student_status="Aktif", pk__in=Extracurricular.objects.select_related('members').values_list('members', flat=True).filter(members__isnull=False).distinct())
        context["inactive_students"] = Student.objects.filter(student_status="Aktif").exclude(id__in=context["active_students"]).order_by("student_class", "student_name")
        context["inactive_students_x"] = Student.objects.filter(student_status="Aktif", student_class__startswith="X-").exclude(id__in=context["active_students"]).order_by("student_class", "student_name")
        context["inactive_students_xi"] = Student.objects.filter(student_status="Aktif", student_class__startswith="XI-").exclude(id__in=context["active_students"]).order_by("student_class", "student_name")
        context["inactive_students_xii"] = Student.objects.filter(student_status="Aktif", student_class__startswith="XII-").exclude(id__in=context["active_students"]).order_by("student_class", "student_name")
        context["active_extracurricular"] = Report.objects.select_related('extracurricular', 'teacher').values_list('extracurricular', flat=True).distinct()
        context["inactive_extracurricular"] = Extracurricular.objects.exclude(id__in=context["active_extracurricular"])
        context["report"] = Report.objects.filter(report_date__month=timezone.now().month).select_related('extracurricular', 'teacher').values('report_date').annotate(dcount=Count('report_date')).distinct().order_by('-report_date')[:11]
        context["report_extracurricular"] = Report.objects.select_related('extracurricular', 'teacher').filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).values('extracurricular__name').annotate(count=Count('extracurricular')).order_by().distinct()
        context["logs"] = UserLog.objects.all()[:10]
        context.update({"object_sebaran": zip(res_sebaran['result']['header'][2:-1], res_sebaran['result']['data'][0][2:-1])})
        context.update({"total_prestasi": res_sebaran['result']['data'][0][-1]})
        context.update({"object_sekolah": res['result']['list']})
        context.update({"object_siswa": res_siswa['result']['list']})
        context.update({"total_data": res_siswa['result']['pagination']['total_data']})
        context.update({"level": level})
        context.update({"year": year})
        return context

class InactiveReportView(ListView):
    model = Report
    template_name = "extracurriculars/extracurricular_inactive_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        active = Report.objects.filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).select_related('extracurricular').values_list('extracurricular', flat=True).distinct()
        data = Extracurricular.objects.exclude(id__in=active)
        return data

    

