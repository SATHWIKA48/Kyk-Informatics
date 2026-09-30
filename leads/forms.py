from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Application


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, label="Full name")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["first_name", "email", "username", "password1", "password2"]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["phone", "resume", "cover_note"]
        labels = {
            "phone": "Phone number",
            "resume": "Resume (PDF or Word, optional)",
            "cover_note": "Why are you a fit for this role?",
        }
        widgets = {
            "cover_note": forms.Textarea(attrs={"rows": 6}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email",
        }
