import datetime
import locale
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.utils import timezone

from laporan.models import Report
from laporan.forms import FormLaporanKehadiran
from ekskul.models import Extracurricular, StudentOrganization, Teacher
from userlog.models import UserLog
from dashboard.whatsapp import send_whatsapp_laporan, send_whatsapp_print

class LaporanIndexView(ListView):
    model = Report
    template_name = 'new_laporan.html'

    def get_queryset(self):
        ekskulList = list()
        for ekskul in Report.objects.filter(tanggal_pembinaan__month=datetime.date.today().month-1).order_by('nama_ekskul__tipe','nama_ekskul__nama_ekskul'):
            if not ekskulList.__contains__(ekskul.nama_ekskul):
                ekskulList.append(ekskul.nama_ekskul)
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return ekskulList
            else:
                return Extracurricular.objects.filter(pembina=self.request.user.teacher).order_by('tipe', 'nama_ekskul')
        else:
            return Extracurricular.objects.all().order_by('tipe', 'nama_ekskul')

class PrintToPDFView(ListView):
    model = Report
    template_name = 'laporan-pdf.html'

    def get_queryset(self):
        return Report.objects.filter(nama_ekskul__slug=self.kwargs.get('slug'), tanggal_pembinaan__month=datetime.date.today().month-1).order_by('tanggal_pembinaan')

    def get_context_data(self, **kwargs):
        context = super(PrintToPDFView, self).get_context_data(**kwargs)
        locale.setlocale(locale.LC_ALL, 'id_ID')
        context['tanggal'] = datetime.datetime.now(timezone.get_default_timezone())
        context['students'] = StudentOrganization.objects.filter(ekskul__slug=self.kwargs.get('slug')).order_by('siswa__kelas', 'siswa__nama_siswa').values_list('siswa__nama_siswa', 'siswa__kelas')
        context['angka'] = [x for x in range(15)]
        ekskul = get_object_or_404(Extracurricular, slug=self.kwargs.get('slug'))
        if self.request.user.is_authenticated:
            UserLog.objects.create(
                        user=(self.request.user.teacher or "Anonymous"),
                        action_flag="ADD",
                        app="LAPORAN",
                        message="Berhasil mencetak laporan pertemuan ekskul {}".format(ekskul.nama_ekskul)
                    )
            send_whatsapp_print(self.request.user.teacher.no_hp, 'mencetak', "ekskul/SC", ekskul.nama_ekskul)
        return context

class PrintToPrintView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'laporan-print.html'
    login_url = '/login/'

    def get_queryset(self):
        if self.request.GET.get('bulan'):
            if self.request.GET.get('tahun'):
                return Report.objects.filter(nama_ekskul__slug=self.kwargs.get('slug'), tanggal_pembinaan__month=self.request.GET.get('bulan'), tanggal_pembinaan__year=self.request.GET.get('tahun')).order_by('tanggal_pembinaan')
            else:
                return Report.objects.filter(nama_ekskul__slug=self.kwargs.get('slug'), tanggal_pembinaan__month=self.request.GET.get('bulan'), tanggal_pembinaan__year=datetime.date.today().year).order_by('tanggal_pembinaan')
        else:
            return Report.objects.filter(nama_ekskul__slug=self.kwargs.get('slug'), tanggal_pembinaan__month=datetime.date.today().month-1).order_by('tanggal_pembinaan')

    def get_context_data(self, **kwargs):
        context = super(PrintToPrintView, self).get_context_data(**kwargs)
        locale.setlocale(locale.LC_ALL, 'id_ID')
        context['tanggal'] = datetime.datetime.now(timezone.get_default_timezone())
        context['students'] = StudentOrganization.objects.filter(ekskul__slug=self.kwargs.get('slug')).order_by('siswa__kelas', 'siswa__nama_siswa').values_list('siswa__nama_siswa', 'siswa__kelas')
        context['angka'] = [x for x in range(15)]
        ekskul = get_object_or_404(Extracurricular, slug=self.kwargs.get('slug'))
        UserLog.objects.create(
                        user=(self.request.user.teacher),
                        action_flag="ADD",
                        app="LAPORAN",
                        message="Berhasil mencetak laporan pertemuan ekskul {}".format(ekskul.nama_ekskul)
        )
        send_whatsapp_print(self.request.user.teacher.no_hp, 'mencetak', "ekskul/SC", ekskul.nama_ekskul)
        return context


class LaporanOptions(ListView):
    model = Report
    template_name = 'new_laporan_options.html'
    def get_queryset(self):
        monthName = {0: "bulan", 1:"Januari", 2:"Februari", 3:"Maret", 4:"April", 5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus", 9:"September", 10:"Oktober", 11:"November", 12:"Desember"}
        monthList = list()
        monthSet = set()
        yearSet = set()
        allDict = dict()
        data = Report.objects.filter(nama_ekskul__slug=self.kwargs.get('slug')).order_by('tanggal_pembinaan').values_list('tanggal_pembinaan', flat=True)
        for i in data:
            monthSet.add(i.month)
            yearSet.add(i.year)
        for i in monthSet:
            monthList.append({"nama": monthName.get(i), "value": i})
        allDict["month"] = monthList
        allDict["year"] = list(yearSet)
        return [allDict]
    
    def get_context_data(self, **kwargs):
        context = super(LaporanOptions, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs.get('slug')
        return context

def LaporanOptionsFunc(request, slug):
    data = Report.objects.filter(nama_ekskul__slug=slug).order_by('-tanggal_pembinaan').values_list('tanggal_pembinaan', flat=True)
    monthName = {0: "bulan", 1:"Januari", 2:"Februari", 3:"Maret", 4:"April", 5:"Mei", 6:"Juni", 7:"Juli", 8:"Agustus", 9:"September", 10:"Oktober", 11:"November", 12:"Desember"}
    monthList = list()
    monthSet = set()
    yearSet = set()
    allDict = dict()
    for i in data:
            monthSet.add(i.month)
            yearSet.add(i.year)
    for i in monthSet:
        monthList.append({"nama": monthName.get(i), "value": i})
    allDict["month"] = monthList
    allDict["year"] = list(yearSet)
    context = {"object_list" : [allDict], "slug": slug} if len(monthList) > 0 else {"object_list" : None, "slug": slug}
    return render(request, 'new_laporan_options.html', context)

@login_required(login_url='/login/')
def laporan_ekskul_print_versi2(request, slug):
    ekskul = get_object_or_404(Extracurricular, slug=slug)
    filtered_report = Report.objects.filter(nama_ekskul__slug=slug).order_by('tanggal_pembinaan')
    UserLog.objects.create(
                    user=(request.user.teacher or "Anonymous"),
                    action_flag="ADD",
                    app="LAPORAN",
                    message="Berhasil mencetak laporan pertemuan ekskul {}".format(ekskul.nama_ekskul)
                )
    send_whatsapp_print(request.user.teacher.no_hp, 'mencetak', "ekskul/SC", ekskul.nama_ekskul)
    context = {
        'ekskul': ekskul,
        'filtered_report': filtered_report,
    }
    return render(request, 'laporan-print2.html', context)

class LaporanEkskulView(ListView):
    model = Report
    template_name = 'new_laporan-ekskul.html'
    queryset = Report.objects.all()
    paginate_by = 10

    def get_queryset(self):
        return self.queryset.filter(nama_ekskul__slug=self.kwargs.get('slug')).order_by('-tanggal_pembinaan')

    def get_context_data(self, **kwargs):
        context = super(LaporanEkskulView, self).get_context_data(**kwargs)
        context['ekskul'] = Extracurricular.objects.filter(slug=self.kwargs.get('slug'))
        context['bulan_ini'] = timezone.now().__format__("%B %Y")
        return context


def laporan_ekskul(request, slug):
    ekskul = get_object_or_404(Extracurricular, slug=slug)
    bulan_ini = datetime.date.today().__format__("%B %Y")
    teachers = Teacher.objects.filter(extracurricular=ekskul)
    all = teachers.values_list('user_id', flat=True)
    filtered_report = Report.objects.filter(nama_ekskul__slug=slug).filter(
        tanggal_pembinaan__month=datetime.date.today().month).order_by('tanggal_pembinaan')
    if request.method == "POST":
        bulan = request.POST.get("bulan")
        if bulan != 0:
            filtered_report = Report.objects.filter(nama_ekskul__slug=slug).filter(
                tanggal_pembinaan__month=bulan).order_by('tanggal_pembinaan')
            bulan_ini = None
        else:
            filtered_report = Report.objects.filter(nama_ekskul__slug=slug).filter(
                tanggal_pembinaan__month=datetime.date.today().month).order_by('tanggal_pembinaan')

    # else:
    #     filtered_report = Report.objects.filter(nama_ekskul__slug=slug).order_by('tanggal_pembinaan')

    if request.user.is_authenticated:
        if not request.user.id in all and not request.user.is_superuser:
            # if not request.user.teacher == ekskul.pembina and not request.user.is_superuser:
            context = {
                'ekskul': ekskul,
                'filtered_report': filtered_report,
                'bulan_ini': bulan_ini,
                'display': None,
            }
        else:
            context = {
                'ekskul': ekskul,
                'filtered_report': filtered_report,
                'bulan_ini': bulan_ini,
                'display': True,
            }
    else:
        context = {
            'ekskul': ekskul,
            'filtered_report': filtered_report,
            'bulan_ini': bulan_ini,
            'display': None
        }
    return render(request, 'laporan-ekskul.html', context)


class LaporanDetailView(DetailView):
    model = Report
    template_name = 'new_laporan-detail.html'


@login_required(login_url='/login/')
def laporan_input(request, slug):
    ekskul = get_object_or_404(Extracurricular, slug=slug)
    filtered_student = StudentOrganization.objects.filter(ekskul=ekskul).order_by('siswa__kelas', 'siswa__nama_siswa')
    all = ekskul.pembina.all().values_list('user_id', flat=True)
    if request.user.id not in all and not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))

    nama_ekskul = request.POST.get('nama_ekskul')
    tanggal_pembinaan = request.POST.get('tanggal_pembinaan')
    kehadiran_santri = request.POST.get('kehadiran_santri')
    pembina = request.POST.get('pembina_ekskul')
    image = request.FILES.get('foto')

    if request.method == 'POST':
        try:
            Report.objects.get(tanggal_pembinaan=tanggal_pembinaan, nama_ekskul__slug=slug)
            form = FormLaporanKehadiran(request.POST, request.FILES)
            messages.error(request, "Laporan untuk tanggal ini sudah ada. Silahkan pilih tanggal lain")
        except:
            form = FormLaporanKehadiran(request.POST, request.FILES)
            FormLaporanKehadiran.nama_ekskul = nama_ekskul
            FormLaporanKehadiran.tanggal_pembinaan = tanggal_pembinaan
            FormLaporanKehadiran.kehadiran_santri = kehadiran_santri
            FormLaporanKehadiran.pembina_ekskul = pembina
            FormLaporanKehadiran.foto = image
            if form.is_valid():
                form.save()
                messages.success(request, "Input Laporan berhasil!")
                locale.setlocale(locale.LC_ALL, 'id_ID')
                tanggal = datetime.date.fromisoformat(tanggal_pembinaan).strftime('%d %B %Y')
                UserLog.objects.create(
                    user=request.user.teacher,
                    action_flag="ADD",
                    app="LAPORAN",
                    message="Berhasil menambahkan data laporan pertemuan ekskul {} untuk tanggal {}".format(ekskul,
                                                                                                            tanggal)
                )

                send_whatsapp_laporan(request.user.teacher.no_hp, ekskul, 'menambahkan', tanggal)
                return redirect('laporan:laporan-input', ekskul.slug)

    else:
        form = FormLaporanKehadiran()

    context = {
        'ekskul': ekskul,
        'filtered_student': filtered_student,
        'form': form,
    }
    return render(request, 'new_laporan-input.html', context)


@login_required(login_url='/login/')
def laporan_edit(request, slug, pk):
    ekskul = get_object_or_404(Extracurricular, slug=slug)
    laporan = get_object_or_404(Report, nama_ekskul__slug=slug, id=pk)
    all = ekskul.pembina.all().values_list('user_id', flat=True)
    if request.user.id not in all and not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))

    if request.method == 'POST':
        form = FormLaporanKehadiran(request.POST, request.FILES, instance=laporan)
        if form.is_valid():
            form.save()
            locale.setlocale(locale.LC_ALL, 'id_ID')
            tanggal = datetime.date.fromisoformat(str(laporan.tanggal_pembinaan)).strftime('%d %B %Y')
            UserLog.objects.create(
                user=request.user.teacher,
                action_flag="CHANGE",
                app="LAPORAN",
                message="Berhasil mengubah data laporan pertemuan ekskul {} untuk tanggal {}".format(ekskul,
                                                                                                     tanggal)
            )

            send_whatsapp_laporan(request.user.teacher.no_hp, ekskul, 'edit', tanggal)
            return redirect('laporan:laporan-ekskul', ekskul.slug)
        else:
            messages.error(request, "Mohon input data dengan benar!")
            form = FormLaporanKehadiran(request.POST, instance=laporan)
    else:
        form = FormLaporanKehadiran(instance=laporan)
    context = {
        'ekskul': ekskul,
        'edit': True,
        'form': form,
    }
    return render(request, 'new_laporan-input.html', context)


@login_required(login_url='/login/')
def laporan_delete(request, slug, pk):
    ekskul = get_object_or_404(Extracurricular, slug=slug)
    laporan = get_object_or_404(Report, nama_ekskul__slug=slug, id=pk)
    all = ekskul.pembina.all().values_list('user_id', flat=True)
    if request.user.id not in all and not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))

    if request.method == 'POST':
        locale.setlocale(locale.LC_ALL, 'id_ID')
        tanggal = datetime.date.fromisoformat(str(laporan.tanggal_pembinaan)).strftime('%d %B %Y')

        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DELETE",
            app="LAPORAN",
            message="Berhasil menghapus data laporan pertemuan ekskul {} untuk tanggal {}".format(ekskul,
                                                                                                  tanggal)
        )

        send_whatsapp_laporan(request.user.teacher.no_hp, ekskul, 'menghapus', tanggal)

        laporan.delete()
        return redirect('laporan:laporan-ekskul', ekskul.slug)
    context = {
        'ekskul': ekskul,
        'laporan': laporan,
    }

    return render(request, 'new_laporan-delete.html', context)