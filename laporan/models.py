import os
from uuid import uuid4
from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse
from extracurriculars.models import Extracurricular
from users.models import Teacher
from students.models import Student
from django.utils.deconstruct import deconstructible
from random import randint


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        if instance.report_date:
            filename = '{}_{}_{}.{}'.format(instance.extracurricular.name, instance.report_date, randint(1, 1000000), ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename = PathAndRename('ekskul/laporan')

# Create your models here.
class Report(models.Model):
    extracurricular = models.ForeignKey(Extracurricular, on_delete=models.CASCADE)
    teacher = models.ManyToManyField(Teacher, help_text=_("Ketik nama yang ingin dicari dan pilih. Kamu bisa memilih lebih dari 1 (satu). Untuk menghapusnya, klik nama yang ingin dihapus hingga berwarna biru/terang, lalu tekan delete atau backspace."))
    report_date = models.DateField(_("Report Date"))
    report_notes = models.TextField(_("Notes"), max_length=200, blank=True)
    students = models.ManyToManyField(Student, help_text=_("Ketik nama yang ingin dicari dan pilih. Kamu bisa memilih lebih dari 1 (satu). Untuk menghapusnya, klik nama yang ingin dihapus hingga berwarna biru/terang, lalu tekan delete atau backspace."))
    photo = models.ImageField(upload_to=path_and_rename, default='no-image.png', help_text=_("Image must be .jpg/.jpeg/.png format"))
    semester = models.CharField(max_length=7, default=settings.SEMESTER, null=True)
    academic_year = models.CharField(max_length=20, default=settings.TAHUN_AJARAN, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.extracurricular} {self.report_date.strftime('%d %B %Y')}"
    

    def get_absolute_url(self):
        return reverse("extracurricular:report-list")
    
    class Meta:
        ordering = ["-report_date"]
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        db_table = "extracurricular_reports"
        indexes = [
            models.Index(fields=["id","report_date",]),
        ]
