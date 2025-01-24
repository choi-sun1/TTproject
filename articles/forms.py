from django import forms
from django.forms import ClearableFileInput
from .models import Article, ArticleImage

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ArticleForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '제목을 입력하세요',
            'id': 'id_title'
        })
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '내용을 입력하세요',
            'rows': '10',
            'id': 'id_content'
        })
    )
    images = MultipleFileField(  # ClearableFileInput 대신 MultipleFileField 사용
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'id': 'id_images'
        })
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '태그를 쉼표로 구분하여 입력하세요 (예: 서울,맛집,여행)',
            'id': 'id_tags'
        })
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'tags']

    def clean_images(self):
        images = self.files.getlist('images')
        if not images:  # 이미지가 없는 경우
            return []
        if len(images) > 5:
            raise forms.ValidationError("이미지는 최대 5개까지만 업로드할 수 있습니다.")
        return images

    def clean(self):
        cleaned_data = super().clean()
        
        # 제목과 내용이 비어있는지 확인
        if not cleaned_data.get('title'):
            raise forms.ValidationError('제목을 입력해주세요.')
        if not cleaned_data.get('content'):
            raise forms.ValidationError('내용을 입력해주세요.')
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            # 태그 저장
            if self.cleaned_data.get('tags'):
                tags = [tag.strip() for tag in self.cleaned_data['tags'].split(',') if tag.strip()]
                for tag_name in tags:
                    tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
                    instance.tags.add(tag)
                    
        return instance
