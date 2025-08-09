# utils/mixins.py
from datetime import datetime
from io import BytesIO
from django.contrib import messages as django_messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.db.models import Q, Model, Count
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import FileResponse, HttpRequest, HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView
from pandas import read_excel
from typing import Any
from classes.models import Class
from courses.models import Course, Subject
from reports.forms import ReportFormV2, ReportUpdatePetugasForm
from reports.models import Report
from schedules.models import Period, ReporterSchedule, Schedule
from userlog.models import UserLog
from users.models import Teacher
from utils.forms import UploadModelForm
from utils.menu_link import export_menu_link
from xlsxwriter import Workbook
from utils_piket.validate_datetime import get_day, parse_to_date
from utils_piket.whatsapp_albinaa import send_whatsapp_action, send_whatsapp_group, send_whatsapp_report
import calendar


# KELAS DEFAULT UNTUK HALAMAN WAJIB LOGIN DAN PERMISSION
class BaseAuthorizedModelView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Base view for generic model views with shared functionality."""
    raise_exception = False  # Raise PermissionDenied for unauthorized users
    menu_name = ''
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Shared method to enrich context data."""
        data = super().get_context_data(**kwargs)
        model_name = self.kwargs.get("site_title", "").split(" - ")[0].title()
        data.update(self.kwargs)
        data.update({"form_name": model_name})
        data.update(export_menu_link(f"{self.menu_name}"))
        return data


# KELAS DEFAULT UNTUK HALAMAN YANG MENGGUNAKAN QUERY DI LISTVIEW
class BaseModelQueryListView(ListView):
    """Base view for generic model views with shared functionality."""
    model = None
    
    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get("query")
        
        if query:
            match self.model.__qualname__:
                case "Class":
                    queryset = self.model.objects.filter(Q(class_name__icontains=query) | Q(short_class_name__icontains=query))
                    return queryset
                case "Course":
                    queryset = self.model.objects.select_related("teacher").filter(Q(course_name__icontains=query) | Q(course_code__icontains=query) | Q(category__icontains=query) | Q(teacher__teacher_name__icontains=query))
                    return queryset
                case "User":
                    queryset = self.model.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
                    return queryset
                case _:
                    raise Http404("Model dalam ListView tidak ditemukan!")
        return super().get_queryset()
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get('query')
        return context