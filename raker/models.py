import os
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.text import slugify
from students.models import Student
from users.models import Teacher


class LaporanPertanggungJawaban(models.Model):
    program = models.CharField(_("Nama Program"), max_length=255)
    tujuan = models.TextField(_("Tujuan Program"), max_length=1000)
    indikator = models.TextField(_("Indikator Keberhasilan"), max_length=1000)
    waktu_pelaksanaan = models.CharField(_("Waktu Pelaksanaan"), max_length=255)
    status = models.CharField(_("Status Pelaksanaan"), max_length=255)
    capaian = models.TextField(_("Capaian Program"), max_length=1000)
    keterangan = models.TextField(_("Keterangan"), max_length=1000, blank=True, null=True)
    penanggungjawab = models.CharField(_("Penanggung Jawab"), max_length=255, blank=True, null=True)
    pengeluaran = models.CharField(_("Pengeluaran"), max_length=255, blank=True, null=True)
    tahun_ajaran = models.CharField(_("Tahun Ajaran"), max_length=40, default=settings.TAHUN_AJARAN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.program} {self.tahun_ajaran}"
    
    def get_absolute_url(self):
        return reverse("lpj")

    class Meta:
        ordering = ["program"]
        verbose_name = _("LPJ")
        verbose_name_plural = _("LPJ")
        db_table = "lpj"
        indexes = [
            models.Index(fields=["id", "program",]),
        ]


class ProgramKerja(models.Model):
    program = models.CharField(_("Nama Program"), max_length=255)
    tujuan = models.TextField(_("Tujuan Program"), max_length=1000)
    indikator = models.TextField(_("Indikator Keberhasilan"), max_length=1000)
    waktu_pelaksanaan = models.CharField(_("Waktu Pelaksanaan"), max_length=255)
    keterangan = models.TextField(_("Keterangan"), max_length=1000, blank=True, null=True)
    penanggungjawab = models.CharField(_("Penanggung Jawab"), max_length=255, blank=True, null=True)
    anggaran = models.CharField(_("Anggaran"), max_length=255, blank=True, null=True)
    tahun_ajaran = models.CharField(_("Tahun Ajaran"), max_length=40, default=settings.TAHUN_AJARAN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.program} {self.tahun_ajaran}"
    
    def get_absolute_url(self):
        return reverse("lpj")

    class Meta:
        ordering = ["program"]
        verbose_name = _("Proker")
        verbose_name_plural = _("Proker")
        db_table = "proker"
        indexes = [
            models.Index(fields=["id", "program",]),
        ]