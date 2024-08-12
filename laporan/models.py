from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse
from extracurriculars.models import Extracurricular
from users.models import Teacher
from students.models import Student

# Create your models here.
class Report(models.Model):
    extracurricular = models.ForeignKey(Extracurricular, on_delete=models.CASCADE)
    teacher = models.ManyToManyField(Teacher)
    report_date = models.DateField(_("Report Date"))
    report_notes = models.TextField(_("Notes"), max_length=200, blank=True)
    students = models.ManyToManyField(Student)
    photo = models.ImageField(upload_to='ekskul/laporan', default='no-image.png', help_text=_("Image must be .jpg/.jpeg/.png format"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.extracurricular} {self.report_date}"
    

    def get_absolute_url(self):
        return reverse("report-list")
    
    class Meta:
        ordering = ["-report_date"]
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        db_table = "reports"
        indexes = [
            models.Index(fields=["id","report_date",]),
        ]
