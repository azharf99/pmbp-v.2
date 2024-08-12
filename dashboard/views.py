from typing import Any
from django.http import FileResponse, HttpRequest, HttpResponse
from django.db.models import Count, QuerySet
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from utils.whatsapp import send_WA_general
from extracurriculars.models import Extracurricular
from students.models import Student
from laporan.models import Report
from prestasi.models import Prestasi
from userlog.models import UserLog
from io import BytesIO
import xlsxwriter

# Create your views here.
class HomeView(ListView):
    model = Prestasi
    template_name = 'index.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Prestasi.objects.exclude(photo='no-image.png')[:12]
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['ekskul'] = Extracurricular.objects.prefetch_related('teacher').order_by('type', 'name')
        context['kegiatan'] = Report.objects.exclude(photo='no-image.png').select_related('extracurricular')[:12]
        return context
    
    
class Dashboard(ListView):
    model = Extracurricular
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["extracurricular"] = self.get_queryset().filter(type="Ekskul")
        context["study_club"] = self.get_queryset().filter(type="SC")
        context["students"] = Student.objects.filter(student_status="Aktif")
        context["active_students"] = Extracurricular.objects.select_related('members').values_list('members', flat=True).filter(members__isnull=False).distinct()
        context["inactive_students"] = Student.objects.filter(student_status="Aktif").exclude(id__in=context["active_students"]).order_by("student_class", "student_name")
        context["inactive_students_x"] = Student.objects.filter(student_status="Aktif", student_class__startswith="X-").exclude(id__in=context["active_students"]).order_by("student_class", "student_name")
        context["inactive_students_xi"] = Student.objects.filter(student_status="Aktif", student_class__startswith="XI-").exclude(id__in=context["active_students"]).order_by("student_class", "student_name")
        context["inactive_students_xii"] = Student.objects.filter(student_status="Aktif", student_class__startswith="XII-").exclude(id__in=context["active_students"]).order_by("student_class", "student_name")
        context["active_extracurricular"] = Report.objects.select_related('extracurricular', 'teacher').values_list('extracurricular', flat=True).distinct()
        context["inactive_extracurricular"] = Extracurricular.objects.exclude(id__in=context["active_extracurricular"])
        context["report"] = Report.objects.select_related('extracurricular', 'teacher').values('report_date').annotate(dcount=Count('report_date')).distinct().order_by('-report_date')[:11]
        context["report_extracurricular"] = Report.objects.select_related('extracurricular', 'teacher').filter(report_date__month=timezone.now().month, report_date__year=timezone.now().year).values('extracurricular__name').annotate(count=Count('extracurricular')).distinct()
        context["logs"] = UserLog.objects.all()[:10]
        return context



    

