from django import forms
from courses.models import Course
from schedules.models import ReporterSchedule, Schedule
from users.models import Teacher

class ScheduleForm(forms.ModelForm):
        
    class Meta:
        model = Schedule
        fields = '__all__'
        widgets = {
            'schedule_day': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
            'schedule_time': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
            'schedule_course': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
            'schedule_class': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
            'semester': forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
            'academic_year': forms.TextInput(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
            'type': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
            'teacher': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 shadow-lg"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_course = self.instance.schedule_course if self.instance and self.instance.pk else None
        # Optimize queryset for schedule_course
        course_qs = Course.objects.select_related('teacher', 'course')
        course_qs = course_qs.exclude(course__status="Pekanan")
        if current_course:
            course_qs = course_qs | Course.objects.filter(pk=current_course.pk)
        self.fields['schedule_course'].queryset = course_qs.distinct()
        self.fields['teacher'].queryset = Teacher.objects.select_related('user').filter(status="Aktif")



class ReporterScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimize related queries
        self.fields['reporter'].queryset = Teacher.objects.select_related('user').filter(status="Aktif")

        
    class Meta:
        model = ReporterSchedule
        fields = '__all__'
        widgets = {
            'schedule_day': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'schedule_time': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'reporter': forms.Select(attrs={"class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'time_start': forms.TimeInput(attrs={"type":"time", "class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
            'time_end': forms.TimeInput(attrs={"type":"time", "class": "rounded-md text-black px-2 py-1 border-2 border-blue-500 dark:border-none shadow-lg"}),
        }