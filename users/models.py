import os
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _
from uuid import uuid4
from random import randint
from utils.constants import SCHEDULE_WEEKDAYS
from utils.models import CleanableFileModel
# Create your models here.

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        if instance.user.username:
            filename = '{}_{}.{}'.format(instance.user.username, randint(1, 1000000), ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename = PathAndRename('user')


class Teacher(CleanableFileModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Username",)
    niy = models.IntegerField(default=0, verbose_name='NIY')
    teacher_name = models.CharField(max_length=100, verbose_name="Nama Pembina", help_text="Nama lengkap pembina, misal: Aam Hamdani, S.Pd.")
    short_name = models.CharField(max_length=100, verbose_name="Nama Singkat", blank=True, null=True, help_text="Nama singkat pembina, misal: Aam Hamdani, S.Pd. menjadi Aam")
    gender = models.CharField(max_length=1, choices=(("L", _("Laki-Laki")), ("P", _("Perempuan"))), default="L")
    address = models.CharField(max_length=100, blank=True, null=True, help_text="Alamat lengkap pembina, misal: Jl. Raya No. 123, Jakarta")
    job = models.CharField(max_length=100, blank=True, null=True, help_text="Pekerjaan pembina, misal: Guru Matematika, Kepala Sekolah, dll")
    email = models.EmailField(default='smaitalbinaa.ekskul@outlook.com', blank=True)
    phone = models.CharField(max_length=20, blank=True, default=0, help_text="Nomor telepon pembina, misal: 08123456789")
    photo = models.ImageField(upload_to=path_and_rename, default='blank-profile.png', blank=True, null=True, help_text="format foto .jpg/.jpeg")
    work_area = models.CharField(max_length=20, blank=True, null=True, help_text="Wilayah Kerja guru ini")
    status = models.CharField(max_length=20, blank=True, null=True, default="Aktif", help_text="Status aktif atau tidaknya guru ini")
    day_off = models.CharField(max_length=10, choices=SCHEDULE_WEEKDAYS, default=SCHEDULE_WEEKDAYS[4][0], help_text="The teacher's designated day off.")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.teacher_name
    
    file_field_names = ['photo']

    def get_absolute_url(self):
        return reverse("teacher-list")
    
    class Meta:
        ordering = ["teacher_name"]
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")
        db_table = "teachers"
        indexes = [
            models.Index(fields=["id","niy",]),
        ]