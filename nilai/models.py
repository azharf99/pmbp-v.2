from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from students.models import Student
from extracurriculars.models import Extracurricular

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
    academic_year = models.CharField(max_length=20, default=f"{timezone.now().year}/{timezone.now().year+1}", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} {self.score}"


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