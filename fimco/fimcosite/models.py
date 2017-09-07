from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models

telephone = RegexValidator(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?\-?\d{2,4}){1,3}?$', 'Not a valid phone number.')


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, msisdn, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not msisdn:
            raise ValueError('The phone number must be set')
        profile = self.model(msisdn=msisdn, **extra_fields)
        profile.set_password(password)
        profile.save(using=self._db)
        return profile

    def create_user(self, msisdn, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(msisdn, password, **extra_fields)

    def create_superuser(self, msisdn, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(msisdn, password, **extra_fields)


class Profile(AbstractBaseUser):
    GENDER = (
        ('M', 'MALE'),
        ('F', 'FEMALE'),
        ('O', 'OTHER')
    )
    STATUS = (
        ('PASS', 'SUCCESSFUL'),
        ('FAIL', 'UNSUCCESSFUL'),
        ('DONE', 'PENDING')
    )
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    email = models.EmailField('email address', unique=True)
    msisdn = models.CharField(max_length=12, unique=True, db_index=True, default='NA', validators=[telephone])
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER)
    client_id = models.CharField(max_length=15, unique=True, primary_key=True)
    pin = models.CharField(max_length=4, unique=True, null=True)
    bot_cds = models.CharField(max_length=15, null=True)
    dse_cds = models.CharField(max_length=15, null=True)
    status = models.CharField(max_length=4, choices=STATUS)
    register_date = models.DateTimeField('date joined', auto_now_add=True)
    pochi_id = models.CharField(max_length=20, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'msisdn'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def clean(self):
        self.status = 'DONE'
        # self.register_date = datetime.date
        if self.get_status_display() == 'SUCCESSFUL':
            self.client_id = generate_client_id()
            self.pin = generate_pin()

    def __str__(self):
        return self.pochi_id


def generate_client_id():
    pass


def generate_pin():
    pass


class JointAccount(models.Model):
    # Group ID
    group_name = models.CharField(max_length=30, unique=True)
    purpose = models.CharField(max_length=30, null=True)
    first_admin = models.CharField(max_length=30)
    sec_admin = models.CharField(max_length=30, null=True)
    pochi_id = models.CharField(max_length=20, null=True)
    members = models.ManyToManyField(Profile, through='JointAccountMembers')
    members_count = models.IntegerField()
    created_at = models.DateTimeField()

    def __str__(self):
        return self.group_name


class JointAccountMembers(models.Model):
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    group = models.ForeignKey(JointAccount, related_name='group_members', on_delete=models.CASCADE)
