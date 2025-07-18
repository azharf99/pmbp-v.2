import os
from uuid import uuid4
from django.db import models
from django.utils.deconstruct import deconstructible
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.text import slugify
from students.models import Student
from users.models import Teacher
from utils.models import CleanableFileModel

days = (
        (None, _("Choose training Day")),
        ('Senin', _('Monday')),
        ('Selasa', _('Tuesday')),
        ('Rabu', _('Wednesday')),
        ('Kamis', _('Thursday')),
        ('Jumat', _('Friday')),
        ('Sabtu', _('Saturday')),
        ('Ahad', _('Sunday'))
    )

pilihan_waktu = (
        (None, _("Choose training time")),
        ("Pagi", _("Morning")),
        ("Siang", _("Noon")),
        ("Sore", _("Evening")),
        ("Malam", _("Night")),
    )

jenis = (
        (None, _("Select Type")),
        ("Ekskul", _("Ekstrakurikuler")),
        ("SC", _("Study Club"))
    )




@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        if instance.id:
            filename = '{}.{}'.format(instance.slug, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename = PathAndRename('ekskul/logo')

class Extracurricular(CleanableFileModel):
    name = models.CharField(_("Extracurricular/SC Name"), max_length=50)
    short_name = models.CharField(_("Short Name"), max_length=20, blank=True, null=True)
    teacher = models.ManyToManyField(Teacher, verbose_name=_("Teachers"), help_text=_("Ketik nama yang ingin dicari dan pilih pembimbing. Kamu bisa memilih lebih dari 1 (satu). Untuk menghapusnya, klik nama yang ingin dihapus hingga berwarna biru/terang, lalu tekan delete atau backspace."))
    schedule = models.CharField(_("Schedule"), max_length=15, choices=days)
    time = models.CharField(_("Time"), max_length=15, choices=pilihan_waktu)
    members = models.ManyToManyField(Student, blank=True, verbose_name=_("Members"), help_text=_("Pada PC, Tekan Ctrl + Clik nama santri untuk memilih lebih dari satu. <br> Pada HP, Beri ceklis (✅) untuk menambahkan atau unchecklist untuk menghapusnya."))
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to=path_and_rename, default='no-image.png', blank=True, null=True, help_text="format logo .jpg/.jpeg")
    type = models.CharField(_("Type"), max_length=20, choices=jenis, blank=True)
    category = models.CharField(_("Kategori"), max_length=50, blank=True, null=True)
    slug = models.SlugField(_("Slug"), blank=True)
    status = models.CharField(_("Status"), max_length=20, default="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    file_field_names = ['logo']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("extracurricular-list")

    class Meta:
        ordering = ["name"]
        verbose_name = _("Extracurricular")
        verbose_name_plural = _("Extracurriculars")
        db_table = "extracurriculars"
        indexes = [
            models.Index(fields=["id", "slug",]),
        ]