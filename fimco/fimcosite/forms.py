from django import forms
from django.contrib.auth.models import User
from django.core.validators import *
from django.forms import CheckboxInput

from .models import CorporateProfile

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


class EnquiryForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'contact[name][required]',
            'id': 'contact:name',
            'required': True
        })
    )
    email = forms.EmailField(
        validators=[EmailValidator],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'name': 'contact[email][required]',
            'id': 'contact:email',
            'required': True
        })
    )
    phone = forms.CharField(
        validators=[telephone],
        widget=forms.TextInput(attrs={
            'class': 'form-control masked',
            'name': 'contact[phone][required]',
            'id': 'contact:phone',
            'data-format': '+255999999999',
            'required': True
        })
    )
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'name': 'contact[subject][required]',
            'id': 'contact:subject',
            'required': True
        })
    )
    message = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'name': 'contact[message][required]',
            'id': 'contact:message',
            'rows': '10',
            'required': True
        })
    )
    attachment = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'name': 'contact[attachment][required]',
            'class': 'form-control',
            'id': 'contact:attachment',
            'onchange': 'jQuery(this).next("input").val(this.value)',
            'required': True
        })
    )

    def clean_attachment(self):
        image = self.cleaned_data['attachment']
        if image:
            self.fields['attachment'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['attachment'].widget.attrs['class'] = 'error'
            if image.file.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5mb )")
            return image
        else:
            self.fields['attachment'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['attachment'].widget.attrs['class'] = 'error'
            raise ValidationError("Couldn't read uploaded image")


class IndividualLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number/email address',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'autocomplete': 'off',
            'required': True
        })
    )


class CorporateLoginForm(forms.Form):
    id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter corporate POCHI ID',
            'required': True
        })
    )
    corp_rep = forms.EmailField(
        validators=[EmailValidator],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'autocomplete': 'off',
            'required': True
        })
    )


class RegisterForm1(forms.Form):
    fName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'class': 'required',
            'required': True
        })
    )
    lName = forms.CharField(
        min_length=2,
        max_length=20,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'class': 'required',
            'required': True
        })
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'required',
            'type': 'date',
            'required': True
        })
    )
    gender = forms.ChoiceField(choices=GENDER)
    email = forms.EmailField(
        validators=[EmailValidator],
        widget=forms.EmailInput(attrs={
            'class': 'required',
            'required': True
        })
    )
    phone = forms.CharField(
        validators=[telephone],
        widget=forms.TextInput(attrs={
            'class': 'form-control masked required',
            'data-format': '+255999999999',
            'placeholder': 'Enter telephone',
            'required': True
        })
    )
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'class': 'required',
            'autocomplete': 'off',
            'required': True

        })
    )
    verify = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'class': 'required',
            'required': True

        })
    )

    def __init__(self, *args, **kwargs):
        super(RegisterForm1, self).__init__(*args, **kwargs)

        for _, field in self.fields.iteritems():
            if field in self.errors:
                field.widget.attrs.update({
                    'autofocus': 'autofocus'
                })
                classes = field.widget.attrs.get('class', '')
                classes += ' errors'
                field.widget.attrs['class'] = classes
                break

    def clean(self):
        clean_data = self.cleaned_data
        username = clean_data['phone'].replace('+255', '0', 1)
        if 'phone' in clean_data and User.objects.filter(username=username).exists():
            self.fields['phone'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['phone'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("This phone number is already associated with another user!")
        if 'email' in clean_data and User.objects.filter(email=clean_data['email']).exists():
            self.fields['email'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['email'].widget.attrs['class'] = 'error'
            self.add_error('email', 'Provide another email')
            raise forms.ValidationError("This email is already associated with another user!")
        if 'password' in clean_data and 'verify' in clean_data and clean_data['password'] != clean_data['verify']:
            self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['password'].widget.attrs['class'] = 'error'
            self.fields['verify'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("Passwords must be identical.")

        return clean_data


class RegisterForm2(forms.Form):
    client_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    scanned_id = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'id': 'file',
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)',
            'required': True
        })
    )
    id_choice = forms.ChoiceField(choices=ID_TYPES)
    bot_cds = forms.CharField(required=False)
    dse_cds = forms.CharField(required=False)
    checker = forms.BooleanField(
        widget=CheckboxInput(attrs={
            'class': 'checked-agree',
            'id': 'checker',
            'required': True
        })
    )

    def __init__(self, *args, **kwargs):
        super(RegisterForm2, self).__init__(*args, **kwargs)

        for _, field in self.fields.iteritems():
            if field in self.errors:
                field.widget.attrs.update({
                    'autofocus': 'autofocus'
                })
                break

    def clean_scanned_id(self):
        image = self.cleaned_data['scanned_id']
        if image:
            self.fields['scanned_id'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['scanned_id'].widget.attrs['class'] = 'error'
            if image.size > 5 * 1024 * 1024:
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
    place = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
            'style': 'display: inline; width: auto',
            'placeholder': 'Building no./Plot no.'
        })
    )
    street = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
            'style': 'display: inline; width: auto',
            'placeholder': 'Road/Street'
        })
    )
    address = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
            'style': 'display: inline; width: auto',
            'placeholder': 'P.O. BOX'
        })
    )
    location = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
            'style': 'display: inline; width: auto',
            'placeholder': 'Town/City'
        })
    )

    def __init__(self, *args, **kwargs):
        super(CorporateForm1, self).__init__(*args, **kwargs)

        for _, field in self.fields.iteritems():
            if field in self.errors:
                field.widget.attrs.update({
                    'autofocus': 'autofocus'
                })
                break

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'name' in cleaned_data and CorporateProfile.objects.filter(company_name=cleaned_data['name']).exists():
            self.fields['name'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['name'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("This company name already exists!")

        return cleaned_data


class CorporateForm2(forms.Form):
    bot = forms.CharField(
        min_length=6,
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': False
        })
    )
    dse = forms.CharField(
        min_length=6,
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': False
        })
    )


class CorporateForm3(forms.Form):
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
            'data-format': '+255999999999',
            'placeholder': 'Enter telephone',
            'required': True,
        })
    )
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
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

    def __init__(self, *args, **kwargs):
        super(CorporateForm3, self).__init__(*args, **kwargs)

        for _, field in self.fields.iteritems():
            if field in self.errors:
                field.widget.attrs.update({
                    'autofocus': 'autofocus'
                })
                break

    def clean(self):
        clean_data = self.cleaned_data
        username = clean_data['phone'].replace('+255', '0', 1)
        if 'phone' in clean_data and User.objects.filter(username=username).exists():
            self.fields['phone'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['phone'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("This phone number is already associated with another user!")
        if 'email' in clean_data and User.objects.filter(email=clean_data['email']).exists():
            self.fields['email'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['email'].widget.attrs['class'] = 'error'
            self.add_error('email', 'Provide another email')
            raise forms.ValidationError("This email is already associated with another user!")
        if 'password' in clean_data and 'verify' in clean_data and clean_data['password'] != clean_data['verify']:
            self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['password'].widget.attrs['class'] = 'error'
            self.fields['verify'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("Passwords must be identical.")

        return clean_data


class CorporateForm4(forms.Form):
    license = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'id': 'license',
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)',
            'required': True
        })
    )
    certificate = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'id': 'certificate',
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)',
            'required': True
        })
    )
    id_type = forms.ChoiceField(choices=ID_TYPES)
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
    checker = forms.BooleanField(
        widget=CheckboxInput(attrs={
            'class': 'checked-agree',
            'id': 'checker',
            'required': True
        })
    )

    # def clean_license(self):
    #     license = self.cleaned_data['license']
    #     if license:
    #         if license.file.size > 5 * 1024 * 1024:
    #             self.fields['certificate'].widget.attrs['autofocus'] = 'autofocus'
    #             self.fields['certificate'].widget.attrs['class'] = 'error'
    #             raise ValidationError("Image file too large ( > 5mb )")
    #         return license
    #     else:
    #         self.fields['certificate'].widget.attrs['autofocus'] = 'autofocus'
    #         self.fields['certificate'].widget.attrs['class'] = 'error'
    #         raise ValidationError("Couldn't read uploaded image")
    #
    # def clean_certificate(self):
    #     certificate = self.cleaned_data['certificate']
    #     if certificate:
    #         if certificate.file.size > 5 * 1024 * 1024:
    #             self.fields['certificate'].widget.attrs['autofocus'] = 'autofocus'
    #             self.fields['certificate'].widget.attrs['class'] = 'error'
    #             raise ValidationError("Image file too large ( > 5mb )")
    #         return certificate
    #     else:
    #         self.fields['certificate'].widget.attrs['autofocus'] = 'autofocus'
    #         self.fields['certificate'].widget.attrs['class'] = 'error'
    #         raise ValidationError("Couldn't read uploaded image")

    # def clean_user_id(self):
    #     identity = self.cleaned_data['user_id']
    #     if identity:
    #         if identity.file.size > 5 * 1024 * 1024:
    #             self.fields['user_id'].widget.attrs['autofocus'] = 'autofocus'
    #             self.fields['user_id'].widget.attrs['class'] = 'error'
    #             raise ValidationError("Image file too large ( > 5mb )")
    #         return identity
    #     else:
    #         self.fields['user_id'].widget.attrs['autofocus'] = 'autofocus'
    #         self.fields['user_id'].widget.attrs['class'] = 'error'
    #         raise ValidationError("Couldn't read uploaded image")


class UserCorporateForm(forms.Form):
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
            'data-format': '+255999999999',
            'placeholder': 'Enter telephone',
            'required': True,
        })
    )
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
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
    id_type = forms.ChoiceField(choices=ID_TYPES)
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
    checker = forms.BooleanField(
        widget=CheckboxInput(attrs={
            'class': 'checked-agree',
            'id': 'checker',
            'required': True
        })
    )

    def __init__(self, *args, **kwargs):
        super(UserCorporateForm, self).__init__(*args, **kwargs)

        for _, field in self.fields.iteritems():
            if field in self.errors:
                field.widget.attrs.update({
                    'autofocus': 'autofocus'
                })
                break

    def clean(self):
        clean_data = self.cleaned_data
        username = clean_data['phone'].replace('+255', '0', 1)
        if 'phone' in clean_data and User.objects.filter(username=username).exists():
            self.fields['phone'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['phone'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("This phone number is already associated with another user!")
        if 'email' in clean_data and User.objects.filter(email=clean_data['email']).exists():
            self.fields['email'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['email'].widget.attrs['class'] = 'error'
            self.add_error('email', 'Provide another email')
            raise forms.ValidationError("This email is already associated with another user!")
        if 'password' in clean_data and 'verify' in clean_data and clean_data['password'] != clean_data['verify']:
            self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['password'].widget.attrs['class'] = 'error'
            self.fields['verify'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("Passwords must be identical.")

        return clean_data

    # def clean_user_id(self):
    #     identity = self.cleaned_data['user_id']
    #     if identity:
    #         if identity.file.size > 5 * 1024 * 1024:
    #             self.fields['user_id'].widget.attrs['autofocus'] = 'autofocus'
    #             self.fields['user_id'].widget.attrs['class'] = 'error'
    #             raise ValidationError("Image file too large ( > 5mb )")
    #         return identity
    #     else:
    #         self.fields['user_id'].widget.attrs['autofocus'] = 'autofocus'
    #         self.fields['user_id'].widget.attrs['class'] = 'error'
    #         raise ValidationError("Couldn't read uploaded image")


class BankAccountForm(forms.Form):
    account_name = forms.CharField(
        min_length=2,
        max_length=50,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'class': 'form-control required',
            'required': True,
        })
    )
    account_no = forms.CharField(
        min_length=10,
        max_length=20,
        validators=[validate_slug],
        widget=forms.TextInput(attrs={
            'class': 'form-control required',
            'required': True,
        })
    )
    bank_name = forms.CharField(
        min_length=2,
        max_length=50,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'class': 'form-control required',
            'required': True,
        })
    )
    branch_name = forms.CharField(
        min_length=2,
        max_length=50,
        validators=[alphabetic],
        widget=forms.TextInput(attrs={
            'class': 'form-control required',
            'required': True,
        })
    )
    bank_address = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control required',
            'rows': '10',
            'required': True,
        })
    )
    swift_code = forms.CharField(
        validators=[validate_slug],
        widget=forms.TextInput(attrs={
            'class': 'form-control required',
            'required': True,
        })
    )


class EditProfileForm(forms.Form):
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
    dob = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True,
        })
    )
    gender = forms.ChoiceField(choices=GENDER)
    client_id = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    scanned_id = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'id': 'file',
            'class': 'form-control',
            'onchange': 'jQuery(this).next("input").val(this.value)',
            'required': True
        })
    )
    id_choice = forms.ChoiceField(choices=ID_TYPES)
    email = forms.EmailField(
        max_length=50,
        widget=forms.TextInput(attrs={
         'class': 'form-control',
         'required': True,
        })
    )
    phone = forms.CharField(
        validators=[telephone],
        widget=forms.TextInput(attrs={
            'class': 'form-control masked',
            'data-format': '9999999999',
            'placeholder': 'Enter telephone',
            'required': True,
        })
    )
    bot_cds = forms.CharField(
        min_length=6,
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': False
        })
    )
    dse_cds = forms.CharField(
        min_length=6,
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': False
        })
    )
    password = forms.CharField(
        validators=[validate_slug],
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
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
        clean_data = self.cleaned_data
        username = clean_data['phone'].replace('+255', '0', 1)
        if 'phone' in clean_data and User.objects.filter(username=username).exists():
            self.fields['phone'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['phone'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("This phone number is already associated with another user!")
        if 'email' in clean_data and User.objects.filter(email=clean_data['email']).exists():
            self.fields['email'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['email'].widget.attrs['class'] = 'error'
            self.add_error('email', 'Provide another email')
            raise forms.ValidationError("This email is already associated with another user!")
        if 'password' in clean_data and 'verify' in clean_data and clean_data['password'] != clean_data['verify']:
            self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
            self.fields['password'].widget.attrs['class'] = 'error'
            self.fields['verify'].widget.attrs['class'] = 'error'
            raise forms.ValidationError("Passwords must be identical.")

        return clean_data

    # def clean_scanned_id(self):
    #     image = self.cleaned_data['scanned_id']
    #     if image:
    #         if image.file.size > 5 * 1024 * 1024:
    #             self.fields['scanned_id'].widget.attrs['autofocus'] = 'autofocus'
    #             self.fields['scanned_id'].widget.attrs['class'] = 'error'
    #             raise ValidationError("Image file too large ( > 5mb )")
    #         return image
    #     else:
    #         self.fields['scanned_id'].widget.attrs['autofocus'] = 'autofocus'
    #         self.fields['scanned_id'].widget.attrs['class'] = 'error'
    #         raise ValidationError("Couldn't read uploaded image")
