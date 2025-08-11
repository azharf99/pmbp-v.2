from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from students.models import Student
from tahfidz.models import Tahfidz, Target, Tilawah
from users.models import Teacher

class TahfidzForm(forms.ModelForm):
    class Meta:
        model = Tahfidz
        fields = '__all__'
        widgets = {
            "santri" : forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "pembimbing" : forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "hafalan" : forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "pencapaian_sebelumnya" : forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "pencapaian_sekarang" : forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "catatan" : forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }

class TilawahForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.fields["santri"].queryset = Student.objects.select_related("student_class").filter(student_status="Aktif")
        self.fields["pendamping"].queryset = Teacher.objects.select_related("user").filter(status="Aktif", gender="L")

    class Meta:
        model = Tilawah
        fields = '__all__'
        widgets = {
            "tanggal" : forms.DateInput(attrs={"type": "date", "class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "santri" : forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "kehadiran" : forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "tercapai" : forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "tajwid" : forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "kelancaran" : forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "ayat" : forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "surat" : forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "pendamping" : forms.SelectMultiple(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "target" : forms.NumberInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "target_tilawah" : forms.Select(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "halaman" : forms.NumberInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "catatan" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "semester" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "academic_year" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }
        labels = {
            "surat" : "Nomor Surat Terakhir",
        }


class TargetForm(forms.ModelForm):

    class Meta:
        model = Target
        fields = '__all__'
        widgets = {
            "tanggal" : forms.DateInput(attrs={"type": "date", "class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "nomor_surat" : forms.NumberInput(attrs={"min": "1", "max": "114", "class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "nama_surat" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "ayat" : forms.NumberInput(attrs={"min": "1", "max": "300", "class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "catatan" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "semester" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "academic_year" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }
