from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from extracurriculars.models import Extracurricular
from students.models import Student

# Create your models here.

class Score(models.Model):
    pilih_nilai = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
    )
    extracurricular = models.ForeignKey(Extracurricular, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.CharField(max_length=3, choices=pilih_nilai)
    semester = models.CharField(max_length=7, default=settings.SEMESTER, null=True)
    academic_year = models.CharField(max_length=20, default=settings.TAHUN_AJARAN, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} {self.extracurricular.name} {self.score} {self.semester} {self.academic_year}"


    def get_absolute_url(self):
        return reverse("nilai-list")
    
    class Meta:
        ordering = ["student", "extracurricular"]
        verbose_name = _("Score")
        verbose_name_plural = _("Scores")
        db_table = "scores"
        indexes = [
            models.Index(fields=["id",]),
        ]