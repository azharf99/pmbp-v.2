from django import forms
from tahfidz.models import Tahfidz, Tilawah

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
    class Meta:
        model = Tilawah
        fields = '__all__'
        widgets = {
            "tanggal" : forms.DateInput(attrs={"type": "date", "class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "santri" : forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "tercapai" : forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "pendamping" : forms.SelectMultiple(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "target" : forms.NumberInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "halaman" : forms.NumberInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "catatan" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "semester" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            "academic_year" : forms.TextInput(attrs={"class": "rounded-md text-black dark:text-white px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }
