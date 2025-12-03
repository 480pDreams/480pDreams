from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Leave a comment...',
                'style': 'width: 100%; background: #000; color: #fff; border: 1px solid #333; padding: 10px; font-family: monospace;'
            }),
        }