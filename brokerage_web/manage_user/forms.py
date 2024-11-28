from django import forms
from .models import FileReaderModel

class FileReaderForm(forms.ModelForm):
    class Meta:
        model = FileReaderModel
        fields = '__all__' # I want this file(button) to be styled