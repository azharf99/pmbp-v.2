from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from students.models import Student
from utils.datetime_wtih_tz import get_current_local_date

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=get_current_local_date)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.student.student_name} - {self.timestamp}"


    def get_absolute_url(self):
        return reverse("attendance-list")
    

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = _("Student's Attendance Record")
        verbose_name_plural = _("Student's Attendance Records")
        db_table = "student_attendance"
        indexes = [
            models.Index(fields=["id", "timestamp"]),
        ]