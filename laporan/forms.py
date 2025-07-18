from django import forms
from django.db.models import Prefetch
from extracurriculars.models import Extracurricular
from laporan.models import Report
from students.models import Student
from users.models import Teacher

class ReportForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Example condition: Filter categories based on the user
        extracurricular_data = Extracurricular.objects.prefetch_related("teacher", "members", "members__student_class").filter(teacher=user.teacher)
        teacher_list = extracurricular_data.values_list("teacher", flat=True).distinct()
        member_list = extracurricular_data.values_list("members", flat=True).distinct()
        if user.teacher.id in teacher_list:
            self.fields['extracurricular'].queryset = extracurricular_data
            self.fields['teacher'].queryset = Teacher.objects.select_related("user").filter(pk__in=teacher_list)
            self.fields['students'].queryset = Student.objects.select_related('student_class').filter(student_status="Aktif", pk__in=member_list)


    class Meta:
        model = Report
        fields = ['extracurricular', 'teacher', 'report_date', 'students', 'report_notes', 'photo']
        widgets = {
            'extracurricular': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'teacher': forms.SelectMultiple(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'report_date': forms.DateInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg", 'type': 'date'}),
            'report_notes': forms.Textarea(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'students': forms.SelectMultiple(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }
