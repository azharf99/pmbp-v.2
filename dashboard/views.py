from typing import Any
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.db.models import Count
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from dashboard.whatsapp import send_whatsapp_input_anggota
from ekskul.models import Extracurricular, Student, StudentOrganization
from laporan.models import Report
from nilai.models import Penilaian
from userlog.models import UserLog
from osn.models import LaporanOSN, BidangOSN
from prestasi.models import Prestasi
import datetime
from io import BytesIO
import xlsxwriter

# Create your views here.
class DashBooard(ListView):
    model = Extracurricular
    template_name = 'dashboard.html'
    queryset = Extracurricular.objects.select_related('pembina')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["extracurricular"] = self.get_queryset().filter(tipe="Ekskul")
        context["study_club"] = self.get_queryset().filter(tipe="SC")
        context["students"] = Student.objects.filter(status="Aktif")
        context["active_students"] = StudentOrganization.objects.select_related('ekskul', 'siswa').filter(siswa__status="Aktif").values_list('siswa', flat=True).distinct()
        context["inactive_students"] = Student.objects.filter(status="Aktif").exclude(id__in=context["active_students"]).order_by("kelas", "nama_siswa")
        context["inactive_students_x"] = Student.objects.filter(status="Aktif", kelas__startswith="X-").exclude(id__in=context["active_students"]).order_by("kelas", "nama_siswa")
        context["inactive_students_xi"] = Student.objects.filter(status="Aktif", kelas__startswith="XI-").exclude(id__in=context["active_students"]).order_by("kelas", "nama_siswa")
        context["inactive_students_xii"] = Student.objects.filter(status="Aktif", kelas__startswith="XII-").exclude(id__in=context["active_students"]).order_by("kelas", "nama_siswa")
        context["active_extracurricular"] = Report.objects.select_related('nama_ekskul', 'pembina_ekskul').values_list('nama_ekskul', flat=True).distinct()
        context["inactive_extracurricular"] = Extracurricular.objects.exclude(id__in=context["active_extracurricular"])
        context["report"] = Report.objects.select_related('nama_ekskul', 'pembina_ekskul').values('tanggal_pembinaan').annotate(dcount=Count('tanggal_pembinaan')).distinct().order_by('-tanggal_pembinaan')[:11]
        context["report_extracurricular"] = Report.objects.select_related('nama_ekskul', 'pembina_ekskul').filter(tanggal_pembinaan__month=timezone.now().month, tanggal_pembinaan__year=timezone.now().year).values('nama_ekskul__nama_ekskul').annotate(count=Count('nama_ekskul')).distinct()
        context["logs"] = UserLog.objects.all().order_by('-created_at')[:10]
        return context


class DownloadExcelInactiveStudent(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Student


    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        active_students = StudentOrganization.objects.select_related('ekskul', 'siswa').filter(siswa__status="Aktif").values_list('siswa', flat=True).distinct()
        inactive_students = Student.objects.filter(status="Aktif").exclude(id__in=active_students).order_by("kelas", "nama_siswa")
        
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer)
        worksheet = workbook.add_worksheet()
        worksheet.write_row(0, 0, ['No', 'Nama Santri', 'Kelas'])
        row = 1
        col = 0
        for data in inactive_students:
            worksheet.write_row(row, col, [row, data.nama_siswa, data.kelas])
            row += 1
        worksheet.autofit()
        workbook.close()
        buffer.seek(0)

        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="PRINT",
            app="DASHBOARD",
            message="Berhasil download data santri tidak aktif ekskul dalam format Excel"
        )
        send_whatsapp_input_anggota(request.user.teacher.no_hp, 'ekskul/SC', 'santri', 'tidak aktif', 'download')

        return FileResponse(buffer, as_attachment=True, filename='Santri Nonaktif Ekskul SMA IT Al Binaa.xlsx')


def dashboard(request):
    ekskul = Extracurricular.objects.all()
    data_ekskul = ekskul.filter(tipe="Ekskul")
    data_sc = ekskul.filter(tipe="SC")
    jumlah_siswa = Student.objects.filter(status="Aktif").count()
    siswa_ekskul = StudentOrganization.objects.select_related('ekskul', 'siswa').values('siswa').annotate(dcount=Count('siswa')).count()
    ekskul_aktif = Report.objects.select_related('nama_ekskul', 'pembina_ekskul').values('nama_ekskul__nama_ekskul').annotate(dcount=Count('nama_ekskul'))
    nama_ekskul = [x['nama_ekskul__nama_ekskul'] for x in ekskul_aktif]
    pertemuan_ekskul = [x['dcount'] for x in ekskul_aktif]
    laporan_ekskul = Report.objects.select_related('nama_ekskul', 'pembina_ekskul').filter(tanggal_pembinaan__month=datetime.datetime.now().month-1).values('tanggal_pembinaan').annotate(dcount=Count('tanggal_pembinaan')).order_by('tanggal_pembinaan')
    laporan = Report.objects.select_related('nama_ekskul', 'pembina_ekskul').order_by('-tanggal_pembinaan')[:20]
    data_pertemuan = [x['dcount'] for x in laporan_ekskul]
    data_tanggal = list(str(x['tanggal_pembinaan'].isoformat()) for x in laporan_ekskul)
    nilai = Penilaian.objects.all().select_related('siswa')
    logs = UserLog.objects.all().order_by('-created_at')[:5]
    osn = LaporanOSN.objects.select_related('pembimbing_osn', 'bidang_osn').values('bidang_osn__nama_bidang').annotate(dcount=Count('bidang_osn')).order_by()
    bidang_osn = list(x['bidang_osn__nama_bidang'] for x in osn)
    pertemuan_osn = list(x['dcount'] for x in osn)
    prestasi = Prestasi.objects.all().order_by('-created_at', '-tahun_lomba', 'peraih_prestasi')[:5]
    bidang_osn_qs = BidangOSN.objects.select_related('pembimbing').order_by('nama_bidang')

    context = {
        'data_ekskul': data_ekskul,
        'data_sc': data_sc,
        'data_ekskul_sc': ekskul.count(),
        'jumlah_siswa': jumlah_siswa,
        'siswa_ekskul': siswa_ekskul,
        'ekskul_aktif': ekskul_aktif.count(),
        'ekskul_nonaktif': (data_ekskul.count() + data_sc.count()) - ekskul_aktif.count(),
        'data_pertemuan': data_pertemuan,
        'data_tanggal': data_tanggal,
        'nilai': nilai,
        'laporan': laporan,
        'logs': logs,
        'bidang_osn': bidang_osn,
        'pertemuan_osn': pertemuan_osn,
        'prestasi': prestasi,
        'nama_ekskul': nama_ekskul,
        'pertemuan_ekskul': pertemuan_ekskul,
        'bidang_osn_qs': bidang_osn_qs,
    }
    return render(request, 'dashboard.html', context)