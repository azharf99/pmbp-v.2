# models.py
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from users.models import Teacher

class Notification(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    title = models.TextField(max_length=100)
    message = models.TextField(max_length=1000)
    type = models.TextField(max_length=20, choices=(("debug", "Debug"), ("info", "Info"), ("success", "Success"), ("warning", "Warning"), ("danger", "Danger")), default="debug")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return f"{self.teacher.teacher_name} | {self.message}"
    

    def get_absolute_url(self):
        return reverse("notification-list")
    

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        db_table = "notifications"
        indexes = [
            models.Index(fields=["id", "teacher"]),
        ]