from django import forms
from olympiads.models import OlympiadField, OlympiadReport
from students.models import Student

class OlympiadFieldForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['members'].queryset = Student.objects.select_related('student_class').filter(student_status="Aktif")
        
    class Meta:
        model = OlympiadField
        fields = '__all__'
        exclude = ['slug']
        widgets = {
            'field_name': forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'teacher': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'schedule': forms.Textarea(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'members': forms.SelectMultiple(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'type': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }

class OlympiadReportForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # # # Example condition: Filter categories based on the user
        data = OlympiadField.objects.select_related("teacher").prefetch_related("members").filter(teacher=user.teacher)
        if user.teacher.id in data.values_list('teacher', flat=True).distinct():
            data_list = data.values_list("members", flat=True).distinct()
            self.fields['students'].queryset = Student.objects.select_related('student_class').filter(pk__in=data_list)
            self.fields['field_name'].queryset = data

    class Meta:
        model = OlympiadReport
        fields = '__all__'
        widgets = {
            'field_name': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'report_date': forms.DateInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg", 'type': 'date'}),
            'students': forms.SelectMultiple(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'notes': forms.Textarea(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }
