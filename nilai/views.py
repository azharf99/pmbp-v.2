from io import BytesIO
from typing import Any
from django.db import models
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
from utils.whatsapp import send_WA_create_update_delete, send_WA_print
import xlsxwriter


# Create your views here.

class NilaiIndexView(ListView):
    model = Score
    paginate_by = 50

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if not self.request.user.is_superuser:
                return Score.objects.filter(extracurricular__teacher=self.request.user.teacher)
        return Score.objects.all()


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
        if Score.objects.filter(student_id = request.POST.get('student')).exists():
            messages.error(request, "Maaf, nilai siswa tersebut sudah terinput!")
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
        extracurricular = Extracurricular.objects.get(id=request.POST.get("extracurricular"))
        for i in range(1, Student.objects.filter(student_status="Aktif").count()+1):
            nilai = request.POST.get(f"score{i}")
            if nilai:
                Score.objects.update_or_create(
                    student_id = request.POST.get(f"student{i}"),
                    extracurricular = extracurricular,
                    defaults={
                        "score": nilai,
                    }
                )
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
        send_WA_print(self.request.user.teacher.phone, 'data nilai', f'Ekskul/SC santri')
        
        return FileResponse(buffer, as_attachment=True, filename='Nilai Ekskul-SC SMA IT Al Binaa.xlsx')