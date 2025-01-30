from django import forms

class ChatForm(forms.Form):
    user_message = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "대화를 시작해보세요!"}),
    )