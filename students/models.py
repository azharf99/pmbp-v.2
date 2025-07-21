import os
from classes.models import Class
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _
from django.utils import timezone
from uuid import uuid4

from utils.models import CleanableFileModel

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        if instance.nis or instance.student_name:
            filename = '{}_{}.{}'.format(instance.nis, instance.student_name, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename = PathAndRename('student')


# Create your models here.
class Student(CleanableFileModel):
    nis = models.CharField(max_length=20, unique=True)
    nisn = models.CharField(max_length=20, blank=True, null=True)
    student_name = models.CharField(max_length=100)
    student_class = models.ForeignKey(Class, on_delete=models.SET_NULL, verbose_name=_("Kelas"), null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(("L", _("Laki-Laki")), ("P", _("Perempuan"))), default="L")
    address = models.CharField(max_length=100, blank=True, null=True)
    student_birth_place = models.CharField(max_length=50, blank=True, null=True)
    student_birth_date = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    student_status = models.CharField(max_length=20, blank=True, default="Aktif")
    photo = models.ImageField(upload_to=path_and_rename, blank=True, null=True, default='blank-profile.png', help_text="Format foto .jpg/.jpeg")
    academic_year = models.CharField(max_length=20, blank=True, null=True, default=f"{timezone.now().year}/{timezone.now().year + 1}")
    face_encoding = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.student_class} | {self.student_name}"
    
    file_field_names = ['photo']

    def get_absolute_url(self):
        return reverse("student-list")

    class Meta:
        ordering = ["student_class__class_name", "student_name"]
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
        db_table = "students"
        indexes = [
            models.Index(fields=["nis", "id",]),
        ]