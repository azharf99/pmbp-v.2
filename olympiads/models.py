from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from users.models import Teacher
from students.models import Student
from django.utils.translation import gettext as _
# Create your models here.

class OlympiadField(models.Model):
    field_name = models.CharField(_("Olympiad Field Name"), max_length=50)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, verbose_name=_("Olympiad's Teacher"))
    schedule = models.TextField(_("Olympiad Field Schedule"), max_length=200)
    members = models.ManyToManyField(Student, blank=True,  verbose_name=_("Olympiad's Students"), help_text=_("Ketik yang ingin dicari dan pilih. Kamu bisa memilih lebih dari 1 (satu). Untuk menghapusnya, klik nama yang ingin dihapus hingga berwarna biru/terang, lalu tekan delete atau backspace."))
    type = models.CharField(_("Olympiad Type"), max_length=50, choices=(("KSM", _("KSM")), ("OSN", _("OSN"))))
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} - {self.field_name}"
    
    def get_absolute_url(self):
        return reverse('olympiad-field-list')
    
    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.type} {self.field_name}")
        super().save(*args, **kwargs)

    
    class Meta:
        ordering = ["type", "field_name"]
        verbose_name = _("Olympiad Field")
        verbose_name_plural = _("Olympiad Fields")
        db_table = "olympiad_fields"
        indexes = [
            models.Index(fields=["id", "slug",]),
        ]


class OlympiadReport(models.Model):
    field_name = models.ForeignKey(OlympiadField, on_delete=models.CASCADE, verbose_name=_("Olympiad Field"))
    report_date = models.DateField(_("Report Date"))
    students = models.ManyToManyField(Student, blank=True, verbose_name=_("Student's Students"), help_text=_("Ketik yang ingin dicari dan pilih. Kamu bisa memilih lebih dari 1 (satu)"))
    report_photo = models.ImageField(_("Report Photo"), upload_to='olimpiade', default='no-image.png', help_text="Format foto harus .jpg atau .jpeg")
    notes = models.TextField(_("Olympiad Notes"), max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.field_name} tanggal {self.report_date}'
    
    def get_absolute_url(self):
        return reverse('olympiad-report-list')
    
    class Meta:
        ordering = ["-report_date"]
        verbose_name = _("Olympiad Report")
        verbose_name_plural = _("Olympiad Reports")
        db_table = "olympiad_reports"
        indexes = [
            models.Index(fields=["id",]),
        ]
