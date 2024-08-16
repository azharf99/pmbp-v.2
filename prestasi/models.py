import os
from uuid import uuid4
from django.db import models
from students.models import Student
from django.urls import reverse
from django.utils.translation import gettext as _

# Create your models here.
def path_and_rename(path):
    def wrapper(instance, filename):
        ext = filename.split('.')[-1]
        # get filename
        if instance.pk:
            filename = '{}_{}_{}_{}.{}'.format(instance.awardee, instance.predicate, instance.name, instance.year, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(path, filename)
    return wrapper


class Prestasi(models.Model):
    category = models.CharField(_("Kategori"), max_length=100)
    type = models.CharField(_("Jenis Lomba"), max_length=100)
    level = models.CharField(_("Tingkat Lomba"), max_length=100)
    year = models.CharField(_("Tahun Lomba"), max_length=4)
    name = models.CharField(_("Nama Lomba"), max_length=100)
    organizer = models.CharField(_("Penyelenggara Lomba"), max_length=100)
    awardee = models.CharField(_("Pemenang"), max_length=100)
    awardee_class = models.CharField(_("Kelas Pemenang"), max_length=100, null=True, blank=True)
    school = models.CharField(_("Sekolah"), max_length=100, default="SMAS IT Al Binaa")
    field = models.CharField(_("Bidang Lomba"), max_length=100)
    predicate = models.CharField(_("Predikat"), max_length=100)
    certificate = models.FileField(_("Serfifikat"), upload_to=path_and_rename('prestasi/sertifikat'), null=True, blank=True)
    photo = models.ImageField(_("Foto"), upload_to=path_and_rename('prestasi'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.awardee} {self.predicate} {self.name} {self.year}"
    
    def get_absolute_url(self):
        return reverse("prestasi-list")

    class Meta:
        ordering = ["-created_at", "-year", "name", "awardee"]
        verbose_name = _("Prestasi")
        verbose_name_plural = _("Prestasi")
        db_table = "prestasi"
        indexes = [
            models.Index(fields=["id",]),
        ]


class ProgramPrestasi(models.Model):
    program_prestasi = models.CharField(_("Program Prestasi"), max_length=200)
    tanggal = models.DateField(_("Tanggal"), )
    nama_peserta = models.ManyToManyField(Student, verbose_name=_("Santri"), help_text=_("Ketik yang ingin dicari dan pilih. Kamu bisa memilih lebih dari 1 (satu)"))
    pencapaian = models.CharField(_("Pencapaian"), max_length=200)
    catatan = models.CharField(_("Catatan"), max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.program_prestasi
    

    def get_absolute_url(self):
        return reverse("program-prestasi-list")

    class Meta:
        ordering = ["-tanggal", "program_prestasi"]
        verbose_name = _("Program Prestasi")
        verbose_name_plural = _("Program Prestasi")
        db_table = "program_prestasi"
        indexes = [
            models.Index(fields=["id",]),
        ]