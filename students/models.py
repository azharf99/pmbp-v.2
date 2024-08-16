import os
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils import timezone
from uuid import uuid4

pilih_kelas = (
        ('X-MIPA-A', 'X-A'),
        ('X-MIPA-B', 'X-B'),
        ('X-MIPA-C', 'X-C'),
        ('X-MIPA-D', 'X-D'),
        ('X-MIPA-E', 'X-E'),
        ('X-MIPA-F', 'X-F'),
        ('X-MIPA-G', 'X-G'),
        ('X-MIPA-H', 'X-H'),
        ('XI-MIPA-A', 'XI-A'),
        ('XI-MIPA-B', 'XI-B'),
        ('XI-MIPA-C', 'XI-C'),
        ('XI-MIPA-D', 'XI-D'),
        ('XI-MIPA-E', 'XI-E'),
        ('XI-MIPA-F', 'XI-F'),
        ('XI-MIPA-G', 'XI-G'),
        ('XI-MIPA-H', 'XI-H'),
        ('XII-MIPA-A', 'XII-A'),
        ('XII-MIPA-B', 'XII-B'),
        ('XII-MIPA-C', 'XII-C'),
        ('XII-MIPA-D', 'XII-D'),
        ('XII-MIPA-E', 'XII-E'),
        ('XII-MIPA-F', 'XII-F'),
        ('XII-MIPA-G', 'XII-G'),
        ('XII-MIPA-H', 'XII-H'),
    )

def path_and_rename(path):
    def wrapper(instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if instance.pk:
            filename = '{}_{}.{}'.format(instance.nis, instance.student_name, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(path, filename)
    return wrapper


# Create your models here.
class Student(models.Model):
    nis = models.CharField(max_length=20, unique=True)
    nisn = models.CharField(max_length=20, blank=True, null=True)
    student_name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=20, choices=pilih_kelas)
    gender = models.CharField(max_length=10, choices=(("L", _("Laki-Laki")), ("P", _("Perempuan"))), default="L")
    address = models.CharField(max_length=100, blank=True, null=True)
    student_birth_place = models.CharField(max_length=50, blank=True, null=True)
    student_birth_date = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    student_status = models.CharField(max_length=20, blank=True, default="Aktif")
    photo = models.ImageField(upload_to=path_and_rename('student'), blank=True, null=True, default='blank-profile.png', help_text="Format foto .jpg/.jpeg")
    academic_year = models.CharField(max_length=20, blank=True, null=True, default=f"{timezone.now().year}/{timezone.now().year + 1}")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.student_class} | {self.student_name}"

    def get_absolute_url(self):
        return reverse("student-list")

    class Meta:
        ordering = ["student_class", "student_name"]
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
        db_table = "students"
        indexes = [
            models.Index(fields=["nis", "id",]),
        ]