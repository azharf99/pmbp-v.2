from django import forms
from dashboard.models import Files, CSVFiles


class FilesForm(forms.ModelForm):
    class Meta:
        model = Files
        fields = '__all__'
        widgets = {
            "file" : forms.FileInput(attrs={"accept": ".xlsx, .xls", "class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
        }


class CSVFilesForm(forms.ModelForm):
    class Meta:
        model = CSVFiles
        fields = '__all__'
        widgets = {
            "file" : forms.FileInput(attrs={"accept": ".csv", "class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
        }