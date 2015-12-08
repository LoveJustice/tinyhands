from django.db import models


class Event(models.Model):
    REPEAT_CHOICES = (
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
    )
    title = models.CharField(max_length=250, verbose_name='Title')
    location = models.CharField(max_length=250, verbose_name='Location', blank=True)
    start_date = models.DateField(verbose_name='Start Date')
    start_time = models.TimeField(verbose_name='Start Time', null=True)
    end_date = models.DateField(verbose_name='End Date')
    end_time = models.TimeField(verbose_name='End Time', null=True)
    description = models.TextField(verbose_name='Description', blank=True)
    is_repeat = models.BooleanField(verbose_name='Repeat', default=False)
    repetition = models.CharField(max_length=50, choices=REPEAT_CHOICES, blank=True, default='')
    ends = models.DateField(verbose_name='Ends At', null=True, blank=True)
    created_on = models.DateTimeField(verbose_name='Crated on', auto_now_add=True, null=True)
    modified_on = models.DateTimeField(verbose_name='Crated on', auto_now=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Event'
