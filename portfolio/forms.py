from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Your Message',
                'required': True
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError("Please enter a valid email address.")
        return email
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        return name

class ReplyForm(forms.Form):
    """Form for replying to contact messages"""
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reply Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Type your reply here...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        original_subject = kwargs.pop('original_subject', '')
        super().__init__(*args, **kwargs)
        if original_subject:
            self.fields['subject'].initial = f"Re: {original_subject}"


from django import forms
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'position', 'company', 'testimonial']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your job title'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'testimonial': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Your testimonial...'
            }),
        }