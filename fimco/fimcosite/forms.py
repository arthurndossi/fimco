from django import forms
from django.contrib.auth.models import User
from django.core.validators import *

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

CORPORATE_IDS = (
    ('tin', 'TIN Number'),
    ('licence', 'Business Licence')
)


class LoginForm(forms.Form):
    username = forms.CharField(
        # validators=[validate_slug],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number/email address',
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
            'required': True
        })
    )
    lName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'required': True
        })
    )
    dob = forms.DateField(
            widget=forms.DateInput(attrs={
                'type': 'date',
                'required': True
            })
    )
    gender = forms.ChoiceField(choices=GENDER)
    client_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control masked',
            'data-placeholder': 'X',
            'required': True
        })
    )
    scanned_id = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'id': 'file', 'required': True})
    )
    id_choice = forms.ChoiceField(choices=ID_TYPES)
    email = forms.EmailField(
        validators=[EmailValidator],
        widget=forms.EmailInput(attrs={
            'required': True
        })
    )
    phone = forms.CharField(
        validators=[telephone],
        widget=forms.TextInput(attrs={
            'class': 'form-control masked',
            'data-format': '0999999999',
            'placeholder': 'Enter telephone',
            'required': True
        })
    )
    bot_cds = forms.CharField(required=False)
    dse_cds = forms.CharField(required=False)
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'required': True

        })
    )
    verify = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'required': True

        })
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'phone' in cleaned_data and User.objects.filter(username=cleaned_data['phone']).exists():
            raise forms.ValidationError("This phone number is already associated with another user!")
        if 'email' in cleaned_data and User.objects.filter(email=cleaned_data['email']).exists():
            raise forms.ValidationError("This email is already associated with another user!")
        if 'password' in cleaned_data and 'verify' in cleaned_data and cleaned_data['password'] != cleaned_data['verify']:
            raise forms.ValidationError("Passwords must be identical.")

        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data['scanned_id']
        if image:
            if image.file.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")


class CorporateForm1(forms.Form):
    name = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
        })
    )
    contact = forms.CharField(
        min_length=10,
        max_length=13,
        validators=[telephone],
        widget=forms.TextInput(attrs={
            'class': 'form-control masked',
            'data-format': '0999999999',
            'placeholder': 'Enter telephone',
            'type': 'tel',
            'required': True,
        })
    )
    address = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'required': True,
        })
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        if User.objects.filter(username=cleaned_data['name']).exists():
            raise forms.ValidationError("This company already exists!")

        return cleaned_data


class CorporateForm2(forms.Form):
    license = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)',
            'required': True
        })
    )
    certificate = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)',
            'required': True
        })
    )


class CorporateForm3(forms.Form):
    bot = forms.CharField(
        min_length=6,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )
    dse = forms.CharField(
        min_length=6,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )


class CorporateForm4(forms.Form):
    fName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
        })
    )
    lName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
        })
    )
    dob = forms.DateField(widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date',
        'required': True,
    }))
    gender = forms.ChoiceField(choices=GENDER)
    email = forms.EmailField(
        validators=[EmailValidator],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'required': True,
        })
    )
    phone = forms.CharField(
        validators=[telephone],
        widget=forms.TextInput(attrs={
            'class': 'form-control masked',
            'data-format': '0999999999',
            'placeholder': 'Enter telephone',
            'required': True,
        })
    )
    id_type = forms.ChoiceField(choices=CORPORATE_IDS)
    id_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    user_id = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)',
            'required': True
        })
    )
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'required': True,
        })
    )
    verify = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
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


class EditProfileForm(forms.Form):
    fName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'required': True,
        })
    )
    lName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'required': True,
        })
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'required': True,
        })
    )
    gender = forms.ChoiceField(choices=GENDER)
    client_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'required': True
        })
    )
    scanned_id = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'id': 'file', 'required': True})
    )
    id_choice = forms.ChoiceField(choices=ID_TYPES)
    email = forms.EmailField(
        max_length=50,
        widget=forms.TextInput(attrs={
         'required': True,
        })
    )
    phone = forms.CharField(
        validators=[telephone],
        widget=forms.TextInput(attrs={
            'class': 'form-control masked',
            'data-format': '0999999999',
            'placeholder': 'Enter telephone',
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
