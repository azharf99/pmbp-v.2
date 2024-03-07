from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from prestasi.forms import PrestasiInputForm, PrestasiEditForm, DokumentasiPrestasiEditForm, DokumentasiPrestasiInputForm, ProgramPrestasiForm
from prestasi.models import Prestasi, DokumentasiPrestasi, ProgramPrestasi
from dashboard.whatsapp import send_whatsapp_input_anggota
from django.contrib import messages

from userlog.models import UserLog
from io import BytesIO

import xlsxwriter


# Create your views here.
class PrestasiIndexView(ListView):
    model = Prestasi
    queryset = Prestasi.objects.all().order_by('-created_at', '-tahun_lomba', 'peraih_prestasi')
    paginate_by = 8
    template_name = 'new_prestasi.html'


def prestasi_detail(request, pk):
    data = get_object_or_404(Prestasi, id=pk)
    context = {
        'data': data,
    }
    return render(request, 'new_prestasi-detail.html', context)


def print_to_excel(request):
    nilai = Prestasi.objects.all().order_by('-created_at',
                                             'peraih_prestasi')
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, ['No', 'Peraih Prestasi', 'Kelas', 'Kategori Lomba', 'Jenis Lomba', 'Tingkat Lomba', 'Tahun Lomba', 'Nama Lomba', 'Bidang Lomba', 'Predikat', 'Penyelengggara', 'Sekolah'])
    row = 1
    col = 0
    for data in nilai:
        worksheet.write_row(row, col, [row, data.peraih_prestasi, data.kelas_peraih_prestasi, data.kategori, data.jenis_lomba, data.tingkat_lomba, data.tahun_lomba, data.nama_lomba, data.bidang_lomba, data.kategori_kemenangan, data.Penyelenggara_lomba, data.sekolah])
        row += 1

    worksheet.autofit()
    workbook.close()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='Prestasi SMA IT Al Binaa.xlsx')


def print_to_excel_tahun_ini(request):
    nilai = Prestasi.objects.filter(created_at__gt="2023-07-16").order_by('-created_at',
                                             'peraih_prestasi')
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    worksheet.write_row(0, 0, ['No', 'Peraih Prestasi', 'Kelas', 'Kategori Lomba', 'Jenis Lomba', 'Tingkat Lomba', 'Tahun Lomba', 'Nama Lomba', 'Bidang Lomba', 'Predikat', 'Penyelengggara', 'dibuat'])
    row = 1
    col = 0
    for data in nilai:
        worksheet.write_row(row, col, [row, data.peraih_prestasi, data.kelas_peraih_prestasi, data.kategori, data.jenis_lomba, data.tingkat_lomba, data.tahun_lomba, data.nama_lomba, data.bidang_lomba, data.kategori_kemenangan, data.Penyelenggara_lomba, str(data.created_at)])
        row += 1

    worksheet.autofit()
    workbook.close()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='Prestasi T.A. 23-24 SMA IT Al Binaa.xlsx')


@login_required(login_url="/login/")
def prestasi_input(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))
    if request.method == 'POST':
        data = request.POST.get('nama_lomba')
        forms = PrestasiInputForm(request.POST, request.FILES)
        if forms.is_valid():
            f = forms.save()
            DokumentasiPrestasi.objects.create(
                prestasi=f,
            )
            UserLog.objects.create(
                user=request.user.teacher,
                action_flag="ADD",
                app="PRESTASI",
                message="Berhasil menambahkan data prestasi {}".format(data)
            )
            send_whatsapp_input_anggota(request.user.teacher.no_hp, data, 'data Prestasi', 'prestasi', 'menambahkan')
            return redirect('prestasi:prestasi-index')
        else:
            forms = PrestasiInputForm(request.POST, request.FILES)
            messages.error(request, "Yang kamu isi ada yang salah dalam isiannya. Tolong diperiksa lagi.")
    else:
        forms = PrestasiInputForm()

    context = {
        'forms': forms,
        'prestasi': True,
    }
    return render(request, 'new_prestasi-input.html', context)


@login_required(login_url="/login/")
def prestasi_edit(request, pk):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))
    data = get_object_or_404(Prestasi, id=pk)
    if request.method == 'POST':
        forms = PrestasiEditForm(request.POST, request.FILES, instance=data)
        if forms.is_valid():
            forms.save()
            UserLog.objects.create(
                user=request.user.teacher,
                action_flag="CHANGE",
                app="PRESTASI",
                message="Berhasil mengubah data prestasi {}".format(data)
            )
            send_whatsapp_input_anggota(request.user.teacher.no_hp, data, 'data Prestasi', 'prestasi', 'mengubah')
            return redirect('prestasi:prestasi-index')
        else:
            forms = PrestasiEditForm(request.POST)
            messages.error(request, "Yang kamu isi ada yang salah dalam isiannya. Tolong diperiksa lagi.")
    else:
        forms = PrestasiEditForm(instance=data)

    context = {
        'forms': forms,
        'prestasi': True,
    }
    return render(request, 'new_prestasi-input.html', context)


@login_required(login_url="/login/")
def prestasi_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))
    data = get_object_or_404(Prestasi, id=pk)
    if request.method == 'POST':
        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DELETE",
            app="PRESTASI",
            message="Berhasil menghapus data prestasi {}".format(data)
        )
        send_whatsapp_input_anggota(request.user.teacher.no_hp, data, 'data Prestasi', 'prestasi', 'menghapus')
        data.delete()
        return redirect('prestasi:prestasi-index')

    context = {
        'data': data,
    }
    return render(request, 'prestasi-delete.html', context)


def dokumentasi_prestasi_detail(request, pk):
    data = get_object_or_404(DokumentasiPrestasi, prestasi_id=pk)
    context = {
        'data': data,
    }
    return render(request, 'prestasi-foto-detail.html', context)

@login_required(login_url="/login/")
def dokumentasi_prestasi_input(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))
    if request.method == 'POST':
        data = request.POST.get('prestasi')
        forms = DokumentasiPrestasiInputForm(request.POST, request.FILES)
        if forms.is_valid():
            forms.save()
            UserLog.objects.create(
                user=request.user.teacher,
                action_flag="ADD",
                app="PRESTASI_DOKUMENTASI",
                message="Berhasil menambahkan foto/dokumentasi prestasi dengan id {}".format(data)
            )
            send_whatsapp_input_anggota(request.user.teacher.no_hp, data, 'foto/dokumentasi untuk Prestasi', 'prestasi', 'menambahkan')
            return redirect('prestasi:prestasi-index')
        else:
            forms = DokumentasiPrestasiInputForm(request.POST, request.FILES)
            messages.error(request, "Yang kamu isi ada yang salah dalam isiannya. Tolong diperiksa lagi.")
    else:
        forms = DokumentasiPrestasiInputForm()

    context = {
        'forms': forms,
        'prestasi': True,
    }
    return render(request, 'new_prestasi-input.html', context)


@login_required(login_url="/login/")
def dokumentasi_prestasi_edit(request, pk):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))
    data = get_object_or_404(DokumentasiPrestasi, id=pk)
    if request.method == 'POST':
        forms = DokumentasiPrestasiEditForm(request.POST, request.FILES, instance=data)
        if forms.is_valid():
            forms.save()
            UserLog.objects.create(
                user=request.user.teacher,
                action_flag="CHANGE",
                app="PRESTASI_DOKUMENTASI",
                message="Berhasil mengubah foto/dokumentasi prestasi {}".format(data)
            )
            send_whatsapp_input_anggota(request.user.teacher.no_hp, data, 'foto/dokumentasi untuk Prestasi', 'prestasi', 'mengubah')
            return redirect('prestasi:prestasi-index')
        else:
            forms = DokumentasiPrestasiEditForm(request.POST, request.FILES)
            messages.error(request, "Yang kamu isi ada yang salah dalam isiannya. Tolong diperiksa lagi.")
    else:
        forms = DokumentasiPrestasiEditForm(instance=data)

    context = {
        'forms': forms,
        'prestasi': True,
    }
    return render(request, 'prestasi-foto-input.html', context)


@login_required(login_url="/login/")
def dokumentasi_prestasi_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))
    data = get_object_or_404(DokumentasiPrestasi, id=pk)
    if request.method == 'POST':
        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DELETE",
            app="PRESTASI_DOKUMENTASI",
            message="Berhasil menghapus foto/dokumentasi prestasi {}".format(data)
        )
        send_whatsapp_input_anggota(request.user.teacher.no_hp, data, 'foto/dokumentasi untuk Prestasi', 'prestasi', 'menghapus')
        data.delete()
        return redirect('prestasi:prestasi-index')

    context = {
        'data': data,
    }
    return render(request, 'prestasi-foto-delete.html', context)


class ProgramPrestasiView(ListView):
    model = ProgramPrestasi
    queryset = ProgramPrestasi.objects.all().order_by('-created_at', '-tanggal',)
    paginate_by = 10
    template_name = 'new_program-prestasi.html'


# class ProgramPrestasiInputView(CreateView):
#     model = ProgramPrestasi
#     queryset = ProgramPrestasi.objects.all().order_by('-created_at', '-tanggal',)
#     paginate_by = 10
#     template_name = 'new_program-prestasi.html'

class ProgramPrestasiInputView(LoginRequiredMixin, CreateView):
    model = ProgramPrestasi
    form_class = ProgramPrestasiForm
    login_url = '/login/'
    success_url = reverse_lazy('prestasi:program-prestasi')
    template_name = 'new_prestasi-input.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="ADD",
                app="PRESTASI",
                message="Berhasil menambahkan data program prestasi {}".format(form.instance.program_prestasi)
            )
        send_whatsapp_input_anggota(self.request.user.teacher.no_hp, form.instance.program_prestasi, 'data Program Prestasi', 'prestasi', 'menambahkan')
        return super().form_valid(form)


class ProgramPrestasiUpdateView(LoginRequiredMixin, UpdateView):
    model = ProgramPrestasi
    form_class = ProgramPrestasiForm
    login_url = '/login/'
    success_url = reverse_lazy('prestasi:program-prestasi')
    template_name = 'new_prestasi-input.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        UserLog.objects.create(
                user=self.request.user.teacher,
                action_flag="ADD",
                app="PRESTASI",
                message="Berhasil menambahkan data program prestasi {}".format(form.instance.program_prestasi)
            )
        send_whatsapp_input_anggota(self.request.user.teacher.no_hp, form.instance.program_prestasi, 'data Program Prestasi', 'prestasi', 'mengedit')
        return super().form_valid(form)


@login_required(login_url="/login/")
def program_prestasi_delete(request, pk):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('restricted'))
    data = get_object_or_404(ProgramPrestasi, id=pk)
    if request.method == 'POST':
        UserLog.objects.create(
            user=request.user.teacher,
            action_flag="DELETE",
            app="PRESTASI_DOKUMENTASI",
            message="Berhasil menghapus program prestasi {}".format(data)
        )
        send_whatsapp_input_anggota(request.user.teacher.no_hp, data, 'foto/dokumentasi untuk Prestasi', 'prestasi', 'menghapus')
        data.delete()
        return redirect('prestasi:program-prestasi')

    context = {
        'data': data,
    }
    return render(request, 'new_program-prestasi-delete.html', context)

def program_print_to_excel(request):
    nilai = ProgramPrestasi.objects.all().order_by('-created_at')
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    merge_format = workbook.add_format({
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
    })
    title_format = workbook.add_format({
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "yellow",
    })
    worksheet.merge_range("A1:F1", "Program Prestasi SMA IT Al Binaa Tahun Ajaran 2023-2024", merge_format)
    worksheet.merge_range("A2:F2", "Tahun Ajaran 2023-2024", merge_format)

    worksheet.write_row(3, 0, ['No', 'Program Prestasi', 'Tanggal', 'Nama Peserta', 'Pencapaian', 'Catatan'], title_format)
    row = 4
    num = 1
    col = 0
    for data in nilai:
        for peserta in data.nama_peserta.all():
            worksheet.write_row(row, col, [num, data.program_prestasi, data.tanggal, peserta.nama_siswa, data.pencapaian, data.catatan])
            num += 1
            row += 1

    # Autofit the worksheet.
    worksheet.autofit()
    worksheet.set_column("A:A", 5)
    workbook.close()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='Program Prestasi SMA IT Al Binaa.xlsx')
