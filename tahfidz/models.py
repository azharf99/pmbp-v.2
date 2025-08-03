from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from students.models import Student
from django.urls import reverse
from django.utils import timezone

from users.models import Teacher
from utils.constants import TAHSIN_STATUS_CHOICES

# Create your models here.
class Tahfidz(models.Model):
    santri = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_("Santri"))
    pembimbing = models.CharField(_("Pembimbing"), max_length=255, blank=True, null=True)
    hafalan = models.CharField(_("Juz yang dihafal"), max_length=255)
    pencapaian_sebelumnya = models.CharField(_("Pencapaian Sebelumnya"), max_length=255, blank=True, null=True)
    pencapaian_sekarang = models.CharField(_("Pencapaian Sekarang"), max_length=255, blank=True, null=True)
    catatan = models.CharField(_("Catatan"), max_length=255, blank=True, null=True)
    semester = models.CharField(max_length=7, default=settings.SEMESTER, null=True)
    academic_year = models.CharField(max_length=20, default=settings.TAHUN_AJARAN, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.santri} - {self.hafalan}"
    

    def get_absolute_url(self):
        return reverse("tahfidz:tahfidz-create")
    
    class Meta:
        ordering = ["-santri"]
        verbose_name = _("Tahfidz")
        verbose_name_plural = _("Tahfidz")
        db_table = "tahfidz"
        indexes = [
            models.Index(fields=["id",]),
        ]


# Create your models here.
class Tilawah(models.Model):
    tanggal = models.DateField(_("Tanggal"), default=timezone.datetime.now)
    santri = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_("Santri"))
    kehadiran = models.CharField(_("Kehadiran"), max_length=10, choices=(("Hadir", "Hadir"), ("Sakit", "Sakit"), ("Telat", "Telat"), ("Izin", "Izin"), ("Alpa", "Alpa")), default="Hadir", blank=True, null=True)
    tercapai = models.BooleanField(_("Tercapai?"), max_length=10, choices=((True, "True"), (False, "False")), default=True, blank=True, null=True)
    target = models.PositiveBigIntegerField(_("Target Tilawah Hari Ini"), blank=True, null=True)
    halaman = models.PositiveBigIntegerField(_("Halaman"), blank=True, null=True)
    catatan = models.CharField(_("Catatan"), max_length=255, blank=True, null=True)
    pendamping = models.ManyToManyField(Teacher,_("Pendamping"), max_length=255, blank=True)
    tajwid = models.CharField(_("Tajwid"), max_length=255, blank=True, null=True, choices=TAHSIN_STATUS_CHOICES)
    kelancaran = models.CharField(_("Kelancaran"), max_length=255, blank=True, null=True, choices=TAHSIN_STATUS_CHOICES)
    semester = models.CharField(max_length=7, default=settings.SEMESTER, null=True)
    academic_year = models.CharField(max_length=20, default=settings.TAHUN_AJARAN, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.tanggal} - {self.santri} - {self.halaman}"
    

    def get_absolute_url(self):
        return reverse("tahfidz:tilawah-create")
    
    class Meta:
        unique_together = (
            ('tanggal', 'santri'),
            ('tanggal', 'santri', 'semester', 'academic_year'),
        )
        ordering = ["-tanggal", "santri"]
        verbose_name = _("Tilawah")
        verbose_name_plural = _("Tilawah")
        db_table = "tilawah"
        indexes = [
            models.Index(fields=["id",]),
        ]