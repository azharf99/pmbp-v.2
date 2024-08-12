from django import forms
from prestasi.models import Prestasi, ProgramPrestasi


class PrestasiForm(forms.ModelForm):
    class Meta:
        model = Prestasi
        fields = '__all__'
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'organizer': forms.TextInput(attrs={'class': 'form-control'}),
            'awardee': forms.TextInput(attrs={'class': 'form-control'}),
            'awardee_class': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'field': forms.TextInput(attrs={'class': 'form-control'}),
            'predicate': forms.TextInput(attrs={'class': 'form-control'}),
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