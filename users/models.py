import os
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _
from uuid import uuid4
# Create your models here.

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        if instance.pk:
            filename = '{}.{}'.format(instance.user, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename = PathAndRename('user')


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Username",)
    niy = models.IntegerField(default=0, verbose_name='NIY')
    teacher_name = models.CharField(max_length=100, verbose_name="Nama Pembina")
    gender = models.CharField(max_length=1, choices=(("L", _("Laki-Laki")), ("P", _("Perempuan"))), default="L")
    address = models.CharField(max_length=100, blank=True, null=True)
    job = models.CharField(max_length=100, blank=True)
    email = models.EmailField(default='smaitalbinaa.ekskul@outlook.com', blank=True)
    phone = models.CharField(max_length=20, blank=True, default=0)
    photo = models.ImageField(upload_to=path_and_rename, default='blank-profile.png', blank=True, null=True, help_text="format foto .jpg/.jpeg")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.teacher_name

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