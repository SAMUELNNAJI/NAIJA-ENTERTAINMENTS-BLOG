from django import forms
from .models import Comment

class Comment_Form(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your comment', 'rows': 4}),
        }
        
    