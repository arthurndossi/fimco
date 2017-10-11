from django import forms
from django.core.validators import *
from django.contrib.auth.models import User
from django.forms.widgets import Input

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


class PhoneInput(Input):
    input_type = 'tel'


class LoginForm(forms.Form):
    phone = forms.IntegerField(
        validators=[validate_slug, telephone],
        widget=forms.NumberInput(attrs={
            'type': 'tel',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'type': 'password',
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
        })
    )
    lName = forms.CharField(min_length=2,
                            max_length=20,
                            validators=[alphabetic],
                            widget=forms.TextInput(attrs={
                                'required': True,
                            })
                            )
    dob = forms.DateField(widget=forms.DateInput(attrs={
        'type': 'date',
        'required': True,
    }))
    gender = forms.ChoiceField(choices=GENDER)
    client_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'required': True
        })
    )
    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'id': 'picture', 'required': True})
    )
    scanned_id = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'id': 'file', 'required': True})
    )
    id_choice = forms.ChoiceField(choices=ID_TYPES)
    email = forms.EmailField(max_length=50,
                             widget=forms.TextInput(attrs={
                                 'required': True,
                             })
                             )
    phone = forms.CharField(validators=[telephone],
                            widget=PhoneInput(attrs={
                                'x-autocompletetype': 'tel',
                                'required': True,
                            })
                            )
    bot_cds = forms.CharField(required=False)
    dse_cds = forms.CharField(required=False)
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'required': True,

        })
    )
    verify = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'required': True,

        })
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        if User.objects.filter(username=cleaned_data['phone']).exists():
            raise forms.ValidationError("This phone number is already associated with another user!")
        if 'password' in cleaned_data and 'verify' in cleaned_data and cleaned_data['password'] != cleaned_data['verify']:
            raise forms.ValidationError("Passwords must be identical.")

        return cleaned_data


class JointAccountForm(forms.Form):
    PURPOSE = ('SCHOOL FEES', 'TRAVEL', 'CONDOLENCE', 'WEDDING', 'OTHERS')
    groupName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'required': True,
        })
    )
    purpose = forms.ChoiceField(choices=PURPOSE, widget=forms.TextInput(attrs={}))
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
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'name': 'contact[first_name]',
            'class': 'form-control required'
        })
    )
    lName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'name': 'contact[last_name]',
            'class': 'form-control required'
        })
    )
    email = forms.EmailField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'name': 'contact[email]',
            'class': 'form-control required'
        })
    )
    phone = forms.CharField(
        validators=[telephone],
        widget=PhoneInput(attrs={
            'name': 'contact[phone]',
            'class': 'form-control required'
        })
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'name': 'contact[start_date]',
            'class': 'form-control datepicker required',
            'data-format': 'yyyy-mm-dd',
            'data-lang': 'en',
            'data-RTL': 'false'
        })
    )
    gender = forms.ChoiceField(
        choices=GENDER,
        widget=forms.TextInput(attrs={
           'name': 'contact[position]',
           'class': 'form-control pointer required'
        })
    )
    avatar = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'type': 'file',
            'name': 'contact[attachment]',
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)'
        })
    )
    id_choice = forms.ChoiceField(choices=ID_TYPES)
    id = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'type': 'file',
            'name': 'contact[id_attachment]',
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)'
        })
    )
    id_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'name': 'contact[file]',
            'class': 'form-control',
        })
    )
    bot_account = forms.CharField(
        widget=forms.TextInput(attrs={
            'name': 'contact[bot]',
            'class': 'form-control',
        })
    )
    dse_account = forms.CharField(
        widget=forms.TextInput(attrs={
            'name': 'contact[dse]',
            'class': 'form-control',
        })
    )
