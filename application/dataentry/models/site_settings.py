from django.db import models
from django.contrib.postgres.fields import JSONField


class SiteSettings(models.Model):
    data = JSONField()
    date_time_last_updated = models.DateTimeField(auto_now=True)

    def get_setting_value_by_name(self, setting_name):
        for setting in self.data:
            if setting['name'] == setting_name:
                return setting['value']
        NameError() 

    def get_setting_by_name(self, setting_name):
        for setting in self.data:
            if setting['name'] == setting_name:
                return setting
        NameError()
