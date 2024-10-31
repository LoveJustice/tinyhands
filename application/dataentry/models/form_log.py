from django.db import models
from django.db.models import JSONField
from accounts.models import Account

class FormLog(models.Model):
	date_time = models.DateTimeField(auto_now_add=True)
	performed_by = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
	form_name = models.CharField(max_length=126)
	form_number = models.CharField(max_length=126)
	form_id = models.IntegerField()
	action = models.CharField(max_length=126)
	details=JSONField(null=True)
	request=JSONField(null=True)
	