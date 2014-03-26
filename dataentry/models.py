from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core import validators
import re


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


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)

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
        return self.email

    def get_full_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None):
        pass


def set_weight(self, weight):
    self.weight = weight
    return self
models.BooleanField.set_weight = set_weight


class InterceptionRecord(models.Model):
    WHO_IN_GROUP_CHOICES = (
        (0, 'Alone'),
        (1, 'Husband / Wife'),
        (2, 'Own brother, sister / relative'),
    )
    who_in_group = models.IntegerField('Who is in the group?', choices=WHO_IN_GROUP_CHOICES)

    drugged_or_drowsy = models.BooleanField().set_weight(40)
    meeting_someone_across_border = models.BooleanField().set_weight(30)
    seen_in_last_month_in_nepal = models.BooleanField().set_weight(20)
    traveling_with_someone_not_with_her = models.BooleanField().set_weight(40)
    wife_under_18 = models.BooleanField().set_weight(45)
    married_in_past_2_weeks = models.BooleanField().set_weight(15)
    married_in_past_2_8_weeks = models.BooleanField().set_weight(10)
    less_than_2_weeks_before_eloping = models.BooleanField().set_weight(20)
    between_2_12_weeks_before_eloping = models.BooleanField().set_weight(15)
    caste_not_same_as_relative = models.BooleanField().set_weight(50)
    caught_in_lie = models.BooleanField().set_weight(35)

    def calculate_total(self):
        total = 0
        for field in self._meta.fields:
            if type(field) == models.BooleanField:
                value = getattr(self, field.name)
                if value is True:
                    total += field.weight

        return total
