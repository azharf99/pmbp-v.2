from django import forms
from files.models import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = '__all__'
        widgets = {
            "file" : forms.FileInput(attrs={"accept": ".xlsx, .xls, .csv", "class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
        }