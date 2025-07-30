from django.core.exceptions import ValidationError
from classes.models import Class
from users.models import Teacher
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from utils.constants import COURSE_CATEGORY_CHOICES, GENDER_AREA_TYPE_CHOICES

# Create your models here.
class Subject(models.Model):
    name = models.CharField(_("Nama Pelajaran"), max_length=50)
    short_name = models.CharField(_("Nama Singkat"), max_length=30, default="")
    category = models.CharField(_("Kategori"), max_length=20, choices=COURSE_CATEGORY_CHOICES, default=COURSE_CATEGORY_CHOICES[1][0])
    type = models.CharField(_("Tipe"), max_length=20, choices=GENDER_AREA_TYPE_CHOICES, default=GENDER_AREA_TYPE_CHOICES[1][0])
    status = models.CharField(_("Status Pelajaran"), max_length=50, default="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self):
        return reverse("course-list")
    

    class Meta:
        ordering = ["name"]
        verbose_name = _("Course Subject")
        verbose_name_plural = _("Course Subjects")
        db_table = "subject"
        indexes = [
            models.Index(fields=["id", "name"]),
        ]

# Create your models here.
class Course(models.Model):
    course = models.ForeignKey(Subject, on_delete=models.SET_NULL, related_name='courses', null=True, verbose_name=_("Mata Pelajaran"))
    course_code = models.CharField(_("Kode Pelajaran"), max_length=20, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, related_name='courses', null=True, verbose_name=_("Guru"))
    type = models.CharField(_("Tipe"), max_length=20, choices=GENDER_AREA_TYPE_CHOICES, default=GENDER_AREA_TYPE_CHOICES[1][0])
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, related_name='courses', null=True, verbose_name=_("Kelas"))
    periods_per_week = models.PositiveIntegerField(default=1, help_text="Number of periods this lesson occurs per week (1-4).")
    consecutive_periods_needed = models.PositiveIntegerField(default=1, help_text="Number of consecutive periods for one session (e.g., 2 for a double period).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f"{self.course} | {self.teacher.teacher_name}"
    
    def clean(self):
        # Add validation to ensure consecutive periods make sense
        if self.consecutive_periods_needed > self.periods_per_week:
            raise ValidationError("Consecutive periods needed cannot be greater than total periods per week.")
        if self.periods_per_week % self.consecutive_periods_needed != 0:
            raise ValidationError("Periods per week should be divisible by the consecutive periods needed for simplicity.")
    

    def get_absolute_url(self):
        return reverse("course-list")
    

    class Meta:
        ordering = ["course"]
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        db_table = "courses"
        indexes = [
            models.Index(fields=["id", "course"]),
        ]
    


