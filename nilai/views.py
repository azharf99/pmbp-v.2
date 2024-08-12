from io import BytesIO
from typing import Any
from django.db.models.query import QuerySet
from django.core.exceptions import PermissionDenied
from django.forms import BaseModelForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from nilai.models import Score
from nilai.forms import ScoreForm
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

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in Score.objects.select_related("extracurricular").values_list("extracurricular__teacher", flat=True) or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if Score.objects.filter(student_id = request.POST.get('siswa')).exists():
            messages.error(request, "Maaf, nilai siswa tersebut sudah ada!")
            return redirect(reverse("nilai-create"))
        
        return super().post(request, *args, **kwargs)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Error! Input data ada yang salah!")
        return super().form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="ADD",
            app="NILAI",
            message=f"Berhasil menambahkan data nilai ekskul {self.object}"
        )
        send_WA_create_update_delete(self.request.user.teacher.phone, 'menambahkan', f'data nilai Ekskul/SC {self.object}', 'nilai/', f'detail/{self.object.id}/')
        messages.success(self.request, "Input nilai berhasil!")
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form_name"] = "Create"
        return context


class NilaiUpdateView(LoginRequiredMixin, UpdateView):
    model = Score
    form_class = ScoreForm
    success_url = reverse_lazy("nilai-list")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.teacher in Score.objects.select_related("extracurricular").values_list("extracurricular__teacher", flat=True) or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, "Error! Input data ada yang salah!")
        return super().form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="ADD",
            app="NILAI",
            message=f"Berhasil mengubah data nilai ekskul {self.object}"
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
        if request.user.teacher in Score.objects.select_related("extracurricular").values_list("extracurricular__teacher", flat=True) or self.request.user.is_superuser:
            return super().get(request, *args, **kwargs)
        raise PermissionDenied
    
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        UserLog.objects.create(
            user=self.request.user.teacher,
            action_flag="DELETE",
            app="NILAI",
            message=f"Berhasil menghapus data nilai ekskul {self.object}"
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
            message="Berhasil download nilai semua ekskul/sc dalam format Excel"
        )
        send_WA_print(self.request.user.teacher.phone, 'data nilai', f'Ekskul/SC santri')
        
        return FileResponse(buffer, as_attachment=True, filename='Nilai Ekskul-SC SMA IT Al Binaa.xlsx')