from django import forms
from extracurriculars.models import Extracurricular
from nilai.models import Score
from students.models import Student

class ScoreForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # # # Example condition: Filter categories based on the user
        data = Extracurricular.objects.prefetch_related("teacher", "members").filter(teacher=user.teacher)
        if user.teacher.id in data.values_list('teacher', flat=True).distinct():
            data_list = data.values_list("members", flat=True).distinct()
            self.fields['student'].queryset = Student.objects.filter(pk__in=data_list)
            self.fields['extracurricular'].queryset = data
        
    class Meta:
        model = Score
        fields = '__all__'
        exclude = ["academic_year"]
        widgets = {
            'extracurricular': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'student': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'score': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }

