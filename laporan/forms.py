from django import forms
from extracurriculars.models import Extracurricular
from laporan.models import Report
from students.models import Student
from users.models import Teacher

class ReportForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # # # Example condition: Filter categories based on the user
        data = Extracurricular.objects.prefetch_related("teacher", "members").filter(teacher=user.teacher)
        data2 = Extracurricular.objects.prefetch_related("teacher", "members").filter(pk__in=data.values_list("id", flat=True))
        if user.teacher.id in data.values_list('teacher', flat=True).distinct():
            data_list = data.values_list("members", flat=True).distinct()
            teacher_list = data2.values_list("teacher", flat=True).distinct()
            self.fields['students'].queryset = Student.objects.select_related('student_class').filter(pk__in=data_list)
            self.fields['extracurricular'].queryset = data
            self.fields['teacher'].queryset = Teacher.objects.select_related("user").filter(pk__in=teacher_list)


    class Meta:
        model = Report
        fields = '__all__'
        widgets = {
            'extracurricular': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'teacher': forms.SelectMultiple(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'report_date': forms.DateInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg", 'type': 'date'}),
            'report_notes': forms.Textarea(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'students': forms.SelectMultiple(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'semester': forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'academic_year': forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }
