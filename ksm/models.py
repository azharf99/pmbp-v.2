from django.db import models
from django.urls import reverse
from ekskul.models import Teacher, Student
from ekskul.compress_image import CompressedImageField

# Create your models here.

class BidangKSM(models.Model):
    nama_bidang = models.CharField(max_length=50, verbose_name="Nama Bidang KSM")
    pembimbing = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    jadwal_bimbingan = models.TextField(max_length=200)
    slug = models.SlugField()

    def get_absolute_url(self):
        return reverse('ksm:ksm-index')

    def __str__(self):
        return f"{self.nama_bidang.capitalize()}"


class SiswaKSM(models.Model):
    bidang_ksm = models.ForeignKey(BidangKSM, on_delete=models.CASCADE)
    nama_siswa = models.ForeignKey(Student, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('ksm:ksm-index')

    def __str__(self):
        return f"{self.bidang_ksm.nama_bidang.upper()} | {self.nama_siswa}"

class LaporanKSM(models.Model):
    pembimbing_ksm = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    bidang_ksm = models.ForeignKey(BidangKSM, on_delete=models.CASCADE)
    tanggal_pembinaan = models.DateField()
    kehadiran_santri = models.ManyToManyField(SiswaKSM)
    foto_bimbingan = CompressedImageField(upload_to='ekskul/ksm', default='no-image.png', quality=50, help_text="Format foto harus .jpg atau .jpeg")
    materi_pembinaan = models.TextField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tanggal_pembinaan.__format__("%d %B %Y")} - {self.pembimbing_ksm}'
    
    def get_absolute_url(self):
        return reverse('ksm:ksm-index')
