from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    title = forms.CharField(
        label='제목',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '제목을 입력하세요'
        })
    )
    content = forms.CharField(
        label='내용',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 15,
            'placeholder': '내용을 입력하세요. 마크다운 문법을 사용할 수 있습니다.'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'content']

    def clean_content(self):
        content = self.cleaned_data['content']
        # 저장 시에는 마크다운을 HTML로 변환하지 않음
        return content
