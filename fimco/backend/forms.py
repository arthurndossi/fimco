from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, validate_slug

alphabetic = RegexValidator(r'^[a-zA-Z\s]*$', 'Only alphabetic characters are allowed.')
telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')

CATEGORY = (
    ('support', 'SUPPORT'),
    ('maker', 'MAKER'),
    ('checker', 'CHECKER')
)


class RegisterForm(forms.Form):
    fName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'required': True,
        })
    )
    lName = forms.CharField(min_length=2,
                            max_length=20,
                            validators=[alphabetic],
                            widget=forms.TextInput(attrs={
                                'required': True,
                            })
                            )
    email = forms.EmailField(max_length=50,
                             widget=forms.TextInput(attrs={
                                 'required': True,
                             })
                             )
    category = forms.ChoiceField(choices=CATEGORY)
    username = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'required': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'required': True,

        })
    )
    verify = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'required': True,

        })
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        if User.objects.filter(username=cleaned_data['username']).exists():
            raise forms.ValidationError("This username is already associated with another user!")
        if 'password' in cleaned_data and 'verify' in cleaned_data and cleaned_data['password'] != cleaned_data['verify']:
            raise forms.ValidationError("Passwords must be identical.")

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        validators=[validate_slug],
        widget=forms.TextInput(attrs={
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'required': True
        })
    )
