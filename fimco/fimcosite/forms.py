from django import forms
from django.core.validators import *
from django.contrib.auth.models import User
from django.forms import TextInput

alphabetic = RegexValidator(r'^[a-zA-Z\s]*$', 'Only alphabetic characters are allowed.')
telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')
words = RegexValidator(r'((?:[^A-Za-z\s]|\s)+)', 'Please enter your full name!')
GENDER = (
        ('M', 'MALE'),
        ('F', 'FEMALE'),
        ('O', 'OTHER')
)

ID_TYPES = (
        ('national', 'National ID'),
        ('voting', 'Voting ID'),
        ('driving', 'Driving license'),
        ('passport', 'Passport')
)


class PhoneInput(TextInput):
    input_type = 'tel'


class LoginForm(forms.Form):
    phone = forms.IntegerField(
        validators=[validate_slug],
        widget=forms.NumberInput(attrs={
            'class': 'inputMaterial gray',
            'required': True
        })
    )
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'class': 'inputMaterial gray',
            'required': True
        })
    )


class RegisterForm(forms.Form):
    fName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'required': True,
            'class': "form-control",
        })
    )
    lName = forms.CharField(min_length=2,
                            max_length=20,
                            validators=[alphabetic],
                            widget=forms.TextInput(attrs={
                                'required': True,
                                'class': "form-control",
                            })
                            )
    dob = forms.DateField(widget=forms.DateInput(attrs={
                                'required': True,
                                'class': "form-control",
                            }))
    gender = forms.ChoiceField(choices=GENDER, widget=forms.TextInput(attrs={'class': "form-control"}))
    client_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'id': 'picture'})
    )
    scanned_id = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'id': 'file'})
    )
    id_choice = forms.ChoiceField(choices=ID_TYPES, widget=forms.TextInput(attrs={'class': "form-control"}))
    email = forms.EmailField(max_length=50,
                             widget=forms.TextInput(attrs={
                                'required': True,
                                'class': "form-control"
                             })
                             )
    phone = forms.CharField(validators=[telephone],
                            widget=PhoneInput(attrs={
                                'x-autocompletetype': 'tel',
                                'required': True,
                                'class': "form-control"
                            })
                            )
    bot_cds = forms.CharField()
    dse_cds = forms.CharField()
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'required': True,
            'class': "form-control"
        })
    )
    verify = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'required': True,
            'class': "form-control"
        })
    )


class JointAccountForm(forms.Form):
    PURPOSE = ('SCHOOL FEES', 'TRAVEL', 'CONDOLENCE', 'WEDDING', 'OTHERS')
    groupName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'required': True,
            'class': "form-control",
        })
    )
    purpose = forms.ChoiceField(choices=PURPOSE, widget=forms.TextInput(attrs={'class': "form-control"}))
    admin_id_one = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    admin_id_two = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    # Not sure about group accounts not specified in the doc
    bot_cds = forms.CharField()
    dse_cds = forms.CharField()


class EditProfileForm(forms.Form):
    fName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic]
    )
    mName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic]
    )
    lName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic]
    )
    dob = forms.DateField()
    gender = forms.ChoiceField(choices=GENDER)
    id = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'client',
            'required': True
        })
    )
    email = forms.EmailField(max_length=50)
    phone = forms.CharField(
        validators=[telephone],
        widget=PhoneInput(attrs={
            'x-autocompletetype': 'tel',
            'required': True,
        })
    )
    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'placeholder': 'Upload scanned copy of ID'
        })
    )
    bot_account = forms.CharField()
    dse_account = forms.CharField()

    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(
                'This email address is already in use. Please supply a different email address.')
        return email
