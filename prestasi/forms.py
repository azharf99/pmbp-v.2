from django import forms
from prestasi.models import Prestasi, DokumentasiPrestasi, ProgramPrestasi


class PrestasiInputForm(forms.ModelForm):
    class Meta:
        model = Prestasi
        fields = '__all__'
        widgets = {
            'kategori': forms.TextInput(attrs={'class': 'form-control'}),
            'jenis_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'tingkat_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'tahun_lomba': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nama_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'Penyelenggara_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'peraih_prestasi': forms.TextInput(attrs={'class': 'form-control'}),
            'kelas_peraih_prestasi': forms.TextInput(attrs={'class': 'form-control'}),
            'sekolah': forms.TextInput(attrs={'class': 'form-control'}),
            'bidang_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'kategori_kemenangan': forms.TextInput(attrs={'class': 'form-control'}),
            'dokumentasi': forms.Select(attrs={'class': 'form-select'}),
        }


class PrestasiEditForm(forms.ModelForm):
    class Meta:
        model = Prestasi
        fields = '__all__'
        widgets = {
            'kategori': forms.TextInput(attrs={'class': 'form-control'}),
            'jenis_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'tingkat_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'tahun_lomba': forms.DateInput(attrs={'class': 'form-control'}),
            'nama_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'Penyelenggara_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'peraih_prestasi': forms.TextInput(attrs={'class': 'form-control'}),
            'kelas_peraih_prestasi': forms.TextInput(attrs={'class': 'form-control'}),
            'sekolah': forms.TextInput(attrs={'class': 'form-control'}),
            'bidang_lomba': forms.TextInput(attrs={'class': 'form-control'}),
            'kategori_kemenangan': forms.TextInput(attrs={'class': 'form-control'}),
            'dokumentasi': forms.Select(attrs={'class': 'form-select'}),
        }


class DokumentasiPrestasiInputForm(forms.ModelForm):
    class Meta:
        model = DokumentasiPrestasi
        fields = '__all__'
        widgets = {
            'prestasi': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control'}),
        }


class DokumentasiPrestasiEditForm(forms.ModelForm):
    class Meta:
        model = DokumentasiPrestasi
        fields = '__all__'
        widgets = {
            'prestasi': forms.Select(attrs={'class': 'form-select'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ProgramPrestasiForm(forms.ModelForm):
    class Meta:
        model = ProgramPrestasi
        fields = '__all__'
        widgets = {
            'program_prestasi' : forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal' : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nama_peserta' : forms.SelectMultiple(attrs={'class': 'form-select'}),
            'pencapaian' : forms.TextInput(attrs={'class': 'form-control'}),
            'catatan' : forms.TextInput(attrs={'class': 'form-control'}),
        }