from django.db import models


class SiteSettings(models.Model):
    data = models.JSONField()
    date_time_last_updated = models.DateTimeField(auto_now=True)

    def get_setting_value_by_name(self, setting_name):
        for setting in self.data:
            if setting['name'] == setting_name:
                return setting['value']
        raise ValueError('Setting with name ' + setting_name + ' not found')

    def get_setting_by_name(self, setting_name):
        for setting in self.data:
            if setting['name'] == setting_name:
                return setting
        raise ValueError('Setting with name "' + setting_name + '" not found')
    
    def set_setting_value_by_name(self, setting_name, value):
        found = False
        for setting in self.data:
            if setting['name'] == setting_name:
                setting['value'] = value
                found = True
                break
        
        if not found:
            setting = {'name':setting_name, 'value':value}
            self.data.append(setting)
