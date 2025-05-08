import string
import random

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.urls import reverse

from rest_framework.authtoken.models import Token
from datetime import timedelta
from django.conf import settings


from templated_email import send_templated_mail
from django.conf import settings


class DefaultPermissionsSet(models.Model):
    name = models.CharField(max_length=255, unique=True)
    permission_irf_view = models.BooleanField(default=False)
    permission_irf_add = models.BooleanField(default=False)
    permission_irf_edit = models.BooleanField(default=False)
    permission_irf_delete = models.BooleanField(default=False)
    permission_vif_view = models.BooleanField(default=False)
    permission_vif_add = models.BooleanField(default=False)
    permission_vif_edit = models.BooleanField(default=False)
    permission_vif_delete = models.BooleanField(default=False)
    permission_person_match = models.BooleanField(default=False)
    permission_accounts_manage = models.BooleanField(default=False)
    permission_receive_investigation_alert = models.BooleanField(default=False)
    permission_receive_legal_alert = models.BooleanField(default=False)
    permission_border_stations_view = models.BooleanField(default=False)
    permission_border_stations_add = models.BooleanField(default=False)
    permission_border_stations_edit = models.BooleanField(default=False)
    permission_border_stations_delete = models.BooleanField(default=False)
    permission_address2_manage = models.BooleanField(default=False)
    permission_budget_view = models.BooleanField(default=False)
    permission_budget_add = models.BooleanField(default=False)
    permission_budget_edit = models.BooleanField(default=False)
    permission_budget_delete = models.BooleanField(default=False)
    permission_can_receive_mdf = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def is_used_by_accounts(self):
        return self.accounts.count() > 0

    def email_accounts(self, alert, context={}):
        if alert.is_investigation():
            accounts = self.accounts.filter(permission_receive_investigation_alert=True)
        elif alert.is_legal():
            accounts = self.accounts.filter(permission_receive_legal_alert=True)
        else:
            raise Exception('Alert type must be either legal or investigation')

        for account in accounts:
            account.email_user("alerts/" + alert.email_template, alert, context)


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
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(40))


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    auth0_id = models.CharField(max_length=255, unique=True, null=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    user_designation = models.ForeignKey(DefaultPermissionsSet, related_name='accounts', on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=127, blank=True)
    country_name = models.CharField(max_length=127, blank=True)

    permission_irf_view = models.BooleanField(default=False)
    permission_irf_add = models.BooleanField(default=False)
    permission_irf_edit = models.BooleanField(default=False)
    permission_irf_delete = models.BooleanField(default=False)
    permission_vif_view = models.BooleanField(default=False)
    permission_vif_add = models.BooleanField(default=False)
    permission_vif_edit = models.BooleanField(default=False)
    permission_vif_delete = models.BooleanField(default=False)
    permission_person_match = models.BooleanField(default=False)
    permission_accounts_manage = models.BooleanField(default=False)
    permission_receive_investigation_alert = models.BooleanField(default=False)
    permission_receive_legal_alert = models.BooleanField(default=False)
    permission_border_stations_view = models.BooleanField(default=False)
    permission_border_stations_add = models.BooleanField(default=False)
    permission_border_stations_edit = models.BooleanField(default=False)
    permission_border_stations_delete = models.BooleanField(default=False)
    permission_address2_manage = models.BooleanField(default=False)
    permission_budget_view = models.BooleanField(default=False)
    permission_budget_add = models.BooleanField(default=False)
    permission_budget_edit = models.BooleanField(default=False)
    permission_budget_delete = models.BooleanField(default=False)

    permission_can_receive_mdf = models.BooleanField(default=False)

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

    def email_user(self, template, alert, context={}):
        context['site'] = settings.SITE_DOMAIN
        context['account'] = self
        context['alert'] = alert
        send_templated_mail(
            template_name=template,
            from_email=settings.ADMIN_EMAIL_SENDER,
            recipient_list=[self.email],
            context=context
        )


class AlertManager(models.Manager):
    def send_alert(self, code, context={}):
        Alert.objects.get(code=code).email_permissions_set(context)


class Alert(models.Model):
    LEGAL_CODES = ['fir and dofe against', 'strength of case']
    INVESTIGATION_CODES = ['Name Match', 'Identified Trafficker']

    code = models.CharField(max_length=255, unique=True)
    email_template = models.CharField(max_length=255)

    permissions_group = models.ManyToManyField(DefaultPermissionsSet)
    objects = AlertManager()

    class Meta:
        verbose_name = 'alert'
        verbose_name_plural = 'alerts'

    def __unicode__(self):
        return self.code

    def email_permissions_set(self, context={}):
        for x in self.permissions_group.all():
            x.email_accounts(self, context)

    def is_investigation(self):
        return self.code in self.INVESTIGATION_CODES

    def is_legal(self):
        return self.code in self.LEGAL_CODES

class ExpiringToken(Token):

    """Extend Token to add an expired method."""

    class Meta(object):
        proxy = True

    def expired(self):
        """Return boolean indicating token expiration."""
        now = timezone.now()
        if self.created < now - self.get_lifespan():
            return True
        return False

    def get_lifespan(self):
        try:
            val = settings.EXPIRING_TOKEN_LIFESPAN
        except AttributeError:
            val = timedelta(days=30)

        return val

