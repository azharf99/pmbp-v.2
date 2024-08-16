import os
from uuid import uuid4
from django.db import models
from django.forms import ImageField
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.text import slugify
from students.models import Student
from users.models import Teacher

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


def path_and_rename(path):
    def wrapper(instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if instance.pk:
            filename = '{}.{}'.format(instance.slug, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(path, filename)
    return wrapper


class Extracurricular(models.Model):
    name = models.CharField(_("Extracurricular/SC Name"), max_length=50)
    teacher = models.ManyToManyField(Teacher, verbose_name=_("Teachers"), help_text=_("Ketik nama yang ingin dicari dan pilih pembimbing. Kamu bisa memilih lebih dari 1 (satu). Untuk menghapusnya, klik nama yang ingin dihapus hingga berwarna biru/terang, lalu tekan delete atau backspace."))
    schedule = models.CharField(_("Schedule"), max_length=15, choices=days)
    time = models.CharField(_("Time"), max_length=15, choices=pilihan_waktu)
    members = models.ManyToManyField(Student, blank=True, verbose_name=_("Members"), help_text=_("Ketik nama yang ingin dicari dan pilih anggota ekskul. Kamu bisa memilih lebih dari 1 (satu). Untuk menghapusnya, klik nama yang ingin dihapus hingga berwarna biru/terang, lalu tekan delete atau backspace."))
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to=path_and_rename('ekskul/logo'), default='no-image.png', blank=True, null=True, help_text="format logo .jpg/.jpeg")
    type = models.CharField(_("Type"), max_length=20, choices=jenis, blank=True)
    slug = models.SlugField(_("Slug"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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