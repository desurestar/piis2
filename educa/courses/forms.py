# ruff: noqa: I001
from django import forms
from django.forms.models import inlineformset_factory

from .models import Course, File, Image, Module, Text, Video

ModuleFormSet = inlineformset_factory(
    Course,
    Module,
    fields=['title', 'description'],
    extra=2,
    can_delete=True,
)


class TextForm(forms.ModelForm):
    class Meta:
        model = Text
        fields = ['title', 'content']


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['title', 'file']


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'file']


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'url']

CONTENT_MODEL_MAP = {
    'text': (Text, TextForm),
    'file': (File, FileForm),
    'image': (Image, ImageForm),
    'video': (Video, VideoForm),
}
