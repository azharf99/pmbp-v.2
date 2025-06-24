import datetime
import requests
import json
import os
import xlsxwriter
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.exceptions import PermissionDenied
from django.forms import BaseModelForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect, HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from extracurriculars.models import Extracurricular
from nilai.models import Score
from nilai.forms import ScoreForm
from students.models import Student
from userlog.models import UserLog
from utils.whatsapp import send_WA_create_update_delete, send_WA_general
from django.conf import settings
from django.utils import timezone
from io import BytesIO
from typing import Any

# Create your views here.

class NilaiIndexView(ListView):
    model = Score
    paginate_by = 50

    def get_queryset(self):
        query = self.request.GET.get("query")
        semester = "Ganjil" if timezone.now().month >= 7 else "Genap"
        academic_year = f"{timezone.now().year}/{timezone.now().year + 1}" if timezone.now().month >= 7 else f"{timezone.now().year - 1}/{timezone.now().year}"

        if query:
            return Score.objects.select_related("student", "extracurricular")\
                    .filter(semester=semester, academic_year=academic_year)\
                    .filter(Q(student__student_name__icontains=query) | 
                            Q(student__student_class__icontains=query) | 
                            Q(extracurricular__name__icontains=query))
        if self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                return Score.objects.select_related("student", "extracurricular").filter(extracurricular__teacher=self.request.user.teacher, semester=semester, academic_year=academic_year)
        return Score.objects.select_related("student", "extracurricular").filter(semester=semester, academic_year=academic_year)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["nama"] = self.request.GET.get("nama")
        c["kelas"] = self.request.GET.get("kelas")
        c["semester"] = "Ganjil" if timezone.now().month >= 7 else "Genap"
        c["academic_year"] = f"{timezone.now().year}/{timezone.now().year + 1}" if timezone.now().month >= 7 else f"{timezone.now().year - 1}/{timezone.now().year}"
        
        return c
    


class NilaiDetailView(DetailView):
    model = Score

    

class NilaiCreateView(LoginRequiredMixin, CreateView):
    model = Score
    form_class = ScoreForm
    success_url = reverse_lazy("nilai-create")


    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher.id in Extracurricular.objects.values_list('teacher', flat=True).distinct() or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> models.Model:
        return super().get_object(queryset)
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        student_id = request.POST.get('student')
        extracurricular_id = request.POST.get('extracurricular')
        score_id = request.POST.get('score')
        if Score.objects.filter(student_id=student_id, extracurricular_id=extracurricular_id).exists():
            ext = Extracurricular.objects.get(id=extracurricular_id)
            stud = Student.objects.get(id=student_id)
            Score.objects.update_or_create(
                student=stud,
                extracurricular=ext,
                semester = "Ganjil" if timezone.now().month >= 7 else "Genap",
                defaults={"score": score_id,}
            )
            send_WA_create_update_delete(self.request.user.teacher.phone, 'mengubah', f'data nilai Ekskul/SC {ext} {stud}', 'nilai/')
            messages.success(self.request, "Update nilai berhasil!")
            return redirect(reverse("nilai-create"))
        
        return super().post(request, *args, **kwargs)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Error! Input data ada yang salah!")
        return super().form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="CREATE",
            app="NILAI",
            message=f"berhasil menambahkan data nilai ekskul {self.object}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'data nilai Ekskul/SC {self.object}', 'nilai/', f'detail/{self.object.id}/')
        messages.success(self.request, "Input nilai berhasil!")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form_name"] = "Create"
        return context
    

class NilaiQuickCreateView(LoginRequiredMixin, CreateView):
    model = Score
    form_class = ScoreForm
    template_name = 'nilai/score_create.html'

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher.id in Extracurricular.objects.values_list('teacher', flat=True).distinct() or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        ex_id = request.POST.get("extracurricular")
        extracurricular = Extracurricular.objects.get(id=ex_id)
        data = requests.get(f"https://pmbp.albinaa.sch.id/extracurriculars/get-members/?query={ex_id}")
        # data = requests.get(f"http://127.0.0.1:8000/extracurriculars/get-members/?query={ex_id}")
        response = json.loads(data.text)
        for i in range(1, len(response)+1):
            nilai = request.POST.get(f"score{i}")
            if nilai:
                Score.objects.update_or_create(
                    student_id = request.POST.get(f"student{i}"),
                    extracurricular = extracurricular,
                    semester = "Ganjil" if timezone.now().month >= 7 else "Genap",
                    defaults={
                        "score": nilai,
                    }
                )

        if not response[0]["id"]:
            messages.error(self.request, "Anggota belum ada!")
            return redirect(reverse("nilai-quick-create"))

        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="QUICK CREATE",
            app="NILAI",
            message=f"berhasil menambahkan banyak data nilai ekskul {extracurricular}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan banyak', f'data nilai Ekskul/SC', 'nilai/')
        messages.success(self.request, "Input nilai berhasil!")
        return redirect(reverse("nilai-list"))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context["extracurricular"] = Extracurricular.objects.prefetch_related("teacher", "members").all()
            context["students"] = None
        else:
            context["extracurricular"] = Extracurricular.objects.prefetch_related("teacher", "members").filter(teacher=self.request.user.teacher)
            context["students"] = Student.objects.filter(pk__in=context["extracurricular"].values_list("members", flat=True).distinct())
        return context


class NilaiUpdateView(LoginRequiredMixin, UpdateView):
    model = Score
    form_class = ScoreForm
    success_url = reverse_lazy("nilai-list")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in self.get_object().extracurricular.teacher.all() or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Error! Input data ada yang salah!")
        return super().form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="UPDATE",
            app="NILAI",
            message=f"berhasil mengubah data nilai ekskul {self.object}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'merubah', f'data nilai Ekskul/SC {self.object}', 'nilai/', f'detail/{self.object.id}/')
        messages.success(self.request, "Input nilai berhasil!")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form_name"] = "Update"
        return context


class NilaiDeleteView(LoginRequiredMixin, DeleteView):
    model = Score
    success_url = reverse_lazy("nilai-list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in self.get_object().extracurricular.teacher.all() or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="DELETE",
            app="NILAI",
            message=f"berhasil menghapus data nilai ekskul {self.object}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menghapus', f'data nilai Ekskul/SC {self.object}', 'nilai/')
        messages.success(self.request, "Input nilai berhasil!")
        return super().post(request, *args, **kwargs)
    

class PrintExcelView(LoginRequiredMixin, ListView):
    model = Score

    def get_queryset(self) -> QuerySet[Any]:
        return Score.objects.select_related("student", "extracurricular").order_by('student__student_class', 'student__student_name')
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, ['No', 'Nama Santri', 'Kelas', 'Ekskul', 'Nilai'])
        row = 1
        col = 0
        for data in self.get_queryset():
            worksheet.write_row(row, col, [row, data.student.student_name, data.student.student_class, data.extracurricular.name, data.score])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)

        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="PRINT",
            app="NILAI",
            message="berhasil download nilai semua ekskul/sc dalam format Excel"
        )
        send_WA_general(self.request.user.teacher.phone, 'data nilai', f'Ekskul/SC santri')
        
        return FileResponse(buffer, as_attachment=True, filename='Nilai Ekskul-SC SMA IT Al Binaa.xlsx')
    

class ExtracurricularScore(ListView):
    model = Score
    template_name = "nilai/score_inactive_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        return Score.objects.select_related("student", "extracurricular").values_list("extracurricular", flat=True).distinct().order_by()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        qs = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context["include"] = Extracurricular.objects.filter(id__in=qs)
        context["exclude"] = Extracurricular.objects.exclude(id__in=qs)
        return context


class SyncronizeWithAIS(LoginRequiredMixin, CreateView):
    model = Score
    fields = '__all__'
    template_name = "nilai/syncronize.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        session = requests.Session()
        base_url = settings.URL_POST_NILAI
        file_path = f'progress--{datetime.date.today()}.txt'
        error_path = 'error.txt'
        scores = Score.objects.select_related('extracurricular', 'student').filter(academic_year=settings.TAHUN_AJARAN)

        id_set = set()
        # Check if file exists
        if not os.path.exists(file_path):
            # Create the file if it does not exist
            with open(file_path, 'w') as file:
                pass

        with open(file_path, 'r') as read_progress_file:
            for id in read_progress_file:
                id_set.add("".join(id.strip().split("--")[1:]))

        for score in scores:
            search = f"{score.student.nis}{score.student.student_name}{score.extracurricular.name}{score.score}"
            if search in id_set:
                continue
            with open(file_path, 'a') as score_progress_file:
                score_progress_file.write(f"{timezone.now()}--{score.student.nis}--{score.student.student_name}--{score.extracurricular.name}--{score.score}\n")
            data = {
                "nilai": score.score,
                "nama_eskul_sc_k": score.extracurricular.name,
                "nis_k": score.student.nis,
            }
            res = session.post(base_url, data=data, timeout=5)
            if res.status_code != 200:
                with open(error_path, 'a') as error_file:
                    error_file.write(f"{timezone.now()}--{score.student.nis}--{score.student.student_name}--{score.extracurricular.name}--{score.score}\n")
        messages.success(request, "Sikronisasi Data Nilai Berhasil!")
        return redirect(reverse("nilai-syncronize"))
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        c["error"] = []
        error_path = 'error.txt'

        if not os.path.exists(error_path):
            with open(error_path, 'w') as file:
                pass

        with open(error_path, 'r') as file:
            for data in file:
                c["error"].append(data.strip().split("--"))
        return c
    

    
