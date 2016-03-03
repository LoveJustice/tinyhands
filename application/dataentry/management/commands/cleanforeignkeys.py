from django.core.management.base import BaseCommand
from dataentry.models import *


class Command(BaseCommand):
    help = 'Clean up bogus foreign key values'

    def clean(self, model):
        class_name = model.__name__
        foreign_keys_fixed = 0

        self.stderr.write("Checking {} models".format(class_name))
        for method_name in ('address1',
                            'address2,
                            'victim_address1',
                            'victim_address2',
                            'victim_guardian_address1',
                            'victim_guardian_address2'):
            if method_name not in dir(model):
                self.stderr.write("{} does not have method {}".format(class_name, method_name))
                continue

            method = getattr(model, method_name)
            for instance in model.objects.all():
                try:
                    method.__get__(instance)
                except model.DoesNotExist:
                    missing_id = getattr(instance, method_name + "_id")
                    self.stderr.write("Removed {} {} from {} {}"
                                      .format(method_name, missing_id,
                                              class_name, instance.pk))
                    foreign_keys_fixed += 1
                    method.__set__(instance, None)
                    instance.save()
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)

        return foreign_keys_fixed

    def handle(self, *args, **options):
        foreign_keys_fixed = 0

        foreign_keys_fixed += self.clean(Interceptee)
        foreign_keys_fixed += self.clean(Address2)
        foreign_keys_fixed += self.clean(VictimInterview)
        foreign_keys_fixed += self.clean(VictimInterviewPersonBox)

        self.stderr.write("Checking complete ({} fixed)".format(foreign_keys_fixed))
