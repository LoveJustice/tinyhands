import string
import random

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from templated_email import send_templated_mail
from dreamsuite.settings import ADMIN_EMAIL_SENDER, SITE_DOMAIN


class DefaultPermissionsSet(models.Model):
    name = models.CharField(max_length=255, unique=True)
    permission_irf_view = models.BooleanField(default=False)
    permission_irf_add = models.BooleanField(default=False)
    permission_irf_edit = models.BooleanField(default=False)
    permission_vif_view = models.BooleanField(default=False)
    permission_vif_add = models.BooleanField(default=False)
    permission_vif_edit = models.BooleanField(default=False)
    permission_accounts_manage = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def is_used_by_accounts(self):
        return self.accounts.count() > 0


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        user = self.model(email=email,
                          is_staff=False, is_active=True,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.save(using=self._db)
        return u

def make_activation_key():
    return ''.join(random.choice(string.ascii_letters + string.digits)
                   for i in range(40))

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    user_designation = models.ForeignKey(DefaultPermissionsSet, related_name='accounts')

    permission_irf_view = models.BooleanField(default=False)
    permission_irf_add = models.BooleanField(default=False)
    permission_irf_edit = models.BooleanField(default=False)
    permission_vif_view = models.BooleanField(default=False)
    permission_vif_add = models.BooleanField(default=False)
    permission_vif_edit = models.BooleanField(default=False)
    permission_accounts_manage = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    
    activation_key = models.CharField(
        max_length=40,
        default=make_activation_key
    )
    

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'account'
        verbose_name_plural = 'accounts'

    def __unicode__(self):
        return self.email

    def get_username(self):
        return self.email

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def email_user(self, subject, message, from_email=None):
        pass

    def send_activation_email(self):
        send_templated_mail(
            template_name='new_user_password_link',
            from_email=ADMIN_EMAIL_SENDER,
            recipient_list=[self.email],
            context={
                'site': SITE_DOMAIN,
                'account': self,
            }
        )

class Alert(models.Model):
    code=models.CharField(max_length=255,unique=True)
    email_template=models.CharField(max_length=255)

    accounts = models.ManyToManyField(Account)

    class Meta:
        verbose_name = 'alert'
        verbose_name_plural = 'alertss'

    def __unicode__(self):
        return self.code

    
