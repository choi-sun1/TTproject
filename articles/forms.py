from django import forms
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
            'class': 'title-input',
            'placeholder': '제목을 입력하세요'
        })
    )
    content = forms.CharField(required=False)
    images = MultipleFileField(
        required=False,
        help_text='최대 5개의 이미지를 선택할 수 있습니다.'
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'tag-input',
            'placeholder': '태그를 입력하세요 (쉼표로 구분)'
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

    def save(self, commit=True):
        article = super().save(commit=False)
        article.content_raw = self.cleaned_data.get('content', '')
        article.content_html = self.cleaned_data.get('content', '')
        
        if commit:
            article.save()
        
        return article
