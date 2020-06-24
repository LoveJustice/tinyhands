from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from dataentry.models import *
from accounts.models import Account, DefaultPermissionsSet
import random
import time


class Command(BaseCommand):
    help = 'update private names, phone numbers and scanned files'

    photo_prefix = 'interceptee_photos/'

    # Set of 20 sample animal photos
    sample_photos = [
        'butterfly.jpg', 'flamingo.jpg', 'lamb.jpg', 'lion.jpg', 'monkey2.jpg',
        'owl.jpg', 'stuffedBear2.jpg', 'clownFish.jpg', 'giraffe.jpg', 'leopard.jpg',
        'llama.jpg', 'monkey.jpg', 'squirrel2.jpg', 'stuffedBear.jpg', 'fawn.jpg',
        'jellyfish.jpg', 'lioness.jpg', 'macaw.jpg', 'ostrich.jpg', 'squirrel.jpg']

    # 100 of the most common last names in the United States
    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones',
        'Miller', 'Davis', 'Garcia', 'Rodriguez', 'Wilson',
        'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Hernandez',
        'Moore', 'Martin', 'Jackson', 'Thompson', 'White',
        'Lopez', 'Lee', 'Gonzalez', 'Harris', 'Clark',
        'Lewis', 'Robinson', 'Walker', 'Perez', 'Hall',
        'Young', 'Allen', 'Sanchez', 'Wright', 'King',
        'Scott', 'Green', 'Baker', 'Adams', 'Nelson',
        'Hill', 'Ramirez', 'Campbell', 'Mitchell', 'Roberts',
        'Carter', 'Phillips', 'Evans', 'Turner', 'Torres',
        'Parker', 'Collins', 'Edwards', 'Stewart', 'Flores',
        'Morris', 'Nguyen', 'Murphy', 'Rivera', 'Cook',
        'Rogers', 'Morgan', 'Peterson', 'Cooper', 'Reed',
        'Bailey', 'Bell', 'Gomez', 'Kelly', 'Howard',
        'Ward', 'Cox', 'Diaz', 'Richardson', 'Wood',
        'Watson', 'Brooks', 'Bennett', 'Gray', 'James',
        'Reyes', 'Cruz', 'Hughes', 'Price', 'Myers',
        'Long', 'Foster', 'Sanders', 'Ross', 'Morales',
        'Powell', 'Sullivan', 'Russell', 'Ortiz', 'Jenkins',
        'Gutierrez', 'Perry', 'Butler', 'Barnes', 'Fisher']

    # The 100 most common names given to girls in 2014
    first_names = [
        'Sophia', 'Emma', 'Olivia', 'Ava', 'Isabella',
        'Mia', 'Zoe', 'Lily', 'Emily', 'Madelyn',
        'Madison', 'Chloe', 'Charlotte', 'Aubrey', 'Avery',
        'Abigail', 'Kaylee', 'Layla', 'Harper', 'Ella',
        'Amelia', 'Arianna', 'Riley', 'Aria', 'Hailey',
        'Hannah', 'Aaliyah', 'Evelyn', 'Addison', 'Mackenzie',
        'Adalyn', 'Ellie', 'Brooklyn', 'Nora', 'Scarlett',
        'Grace', 'Anna', 'Isabelle', 'Natalie', 'Kaitlyn',
        'Lillian', 'Sarah', 'Audrey', 'Elizabeth', 'Leah',
        'Annabelle', 'Kylie', 'Mila', 'Claire', 'Victoria',
        'Maya', 'Lila', 'Elena', 'Lucy', 'Savannah',
        'Gabriella', 'Callie', 'Alaina', 'Sophie', 'Makayla',
        'Kennedy', 'Sadie', 'Skyler', 'Allison', 'Caroline',
        'Charlie', 'Penelope', 'Alyssa', 'Peyton', 'Samantha',
        'Liliana', 'Bailey', 'Maria', 'Reagan', 'Violet',
        'Eliana', 'Adeline', 'Eva', 'Stella', 'Keira',
        'Katherine', 'Vivian', 'Alice', 'Alexandra', 'Camilla',
        'Kayla', 'Alexis', 'Sydney', 'Kaelyn', 'Jasmine',
        'Julia', 'Cora', 'Lauren', 'Piper', 'Gianna',
        'Paisley', 'Bella', 'London', 'Clara', 'Cadenc']

    number_strings = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    irf_file_prefix = 'scanned_irf_forms/'
    vif_file_prefix = 'scanned_vif_forms/'

    sample_files = [
        'sample_200dpi.pdf', 'sample_300dpi.pdf', 'sample_400dpi.pdf', 'sample_720dpi.pdf',
        'sample_240dpi.pdf', 'sample_360dpi.pdf', 'sample_600dpi.pdf', 'sample_800dpi.pdf']

    def sanitize(self, model, photo_fields=[], name_fields=[], phone_fields=[], file_fields=[], file_prefix=None, text_fields=[]):
        class_name = model.__name__
        processed = 0

        for instance in model.objects.all():
            modified = False

            # Sanitize images
            for field_name in photo_fields:
                try:
                    value = getattr(instance, field_name)
                    if value is not None:
                        setattr(instance, field_name, self.select_photo())
                        modified = True
                except AttributeError as e:
                    print(e)
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)

            # Sanitize names
            for field_name in name_fields:
                try:
                    value = getattr(instance, field_name)
                    if value is not None:
                        setattr(instance, field_name, self.generate_name())
                        modified = True
                except AttributeError as e:
                    print(e)
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)

            # Sanitize phone numbers
            for field_name in phone_fields:
                try:
                    value = getattr(instance, field_name)
                    if value is not None:
                        setattr(instance, field_name, self.generate_phone(value))
                        modified = True
                except AttributeError as e:
                    print(e)
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)

            # Sanitize scanned files
            for field_name in file_fields:
                try:
                    value = getattr(instance, field_name)
                    if value is not None:
                        setattr(instance, field_name, self.select_file(file_prefix))
                        modified = True
                except AttributeError as e:
                    print(e)
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)
            
            for field_name in test_fields:
                try:
                    value = getattr(instance, field_name)
                    if value is not None:
                        setattr(instance, field_name, 'PRIVATE')
                        modified = True
                except AttributeError as e:
                    print(e)
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)
                    

            if modified:
                instance.save()
                processed += 1

        self.stdout.write("Sanitize model {}: objects processed {}".format(class_name, processed))

        return processed

    def select_photo(self):
        new_photo = self.photo_prefix + random.choice(self.sample_photos)
        return new_photo

    def generate_name(self):
        new_name = random.choice(self.first_names) + \
            ' ' + random.choice(self.last_names)
        return new_name

    def generate_phone(self, old_number):
        phone = ''
        for idx in range(len(old_number)):
            phone = phone + random.choice(self.number_strings)

        return phone

    def select_file(self, prefix):
        new_file = prefix + random.choice(self.sample_files)
        return new_file

    def sanitize_email(self):
        for instance in Account.objects.all():
            instance.email = next(self.get_next_email())
            instance.permission_receive_email = False
            instance.save()

    def get_next_email(self):
        cnt = 0
        while True:
            cnt += 1
            email = "thi_" + str(cnt) + "@example.com"
            if len(Account.objects.filter(email=email)) > 0:
                continue
            yield email

    def create_base_user(self):
        account = Account()
        account.last_name = 'Test'
        localtime = time.localtime()
        account.last_login = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        account.joined = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        account.user_designation_id = 1
        account.is_active = True
        return account

    def add_all_permissions(self, account):

        account.permission_irf_add = True
        account.permission_irf_view = True
        account.permission_irf_edit = True

        account.permission_vif_add = True
        account.permission_vif_view = True
        account.permission_vif_edit = True

        account.permission_receive_email = False

        account.permission_border_stations_add = True
        account.permission_border_stations_view = True
        account.permission_border_stations_edit = True

        account.permission_address2_manage = True

        account.permission_budget_view = True
        account.permission_budget_add = True
        account.permission_budget_edit = True
        account.permission_budget_delete = True

        return account

    def create_super(self):
        account = self.create_base_user()
        account = self.add_all_permissions(account)
        account.is_superuser = True
        account.permission_accounts_manage = True
        account.is_staff = True
        return account

    def create_test_users(self):
        account = self.create_super()
        account.first_name = 'super'
        account.email = 'test_sup@example.com'
        account.set_password('pass')
        try:
            account.save()
        except IntegrityError:
            self.stderr.write("There is an existing user with email {}".format(account.email))

        account = self.create_base_user()
        account = self.add_all_permissions(account)
        account.first_name = 'test1'
        account.email = 'test1@example.com'
        account.set_password('pass')
        try:
            account.save()
        except IntegrityError:
            self.stderr.write("There is an existing user with email {}".format(account.email))

    def handle(self, *args, **options):
        sanitized = 0
        # Clean old forms
        Interceptee.objects.all().delete()
        InterceptionRecord.objects.all().delete()
        VictimInterviewPersonBox.objects.all().delete()
        VictimInterviewLocationBox.objects.all().delete()
        victimInterview.objects.all().delete()

        sanitized += self.sanitize(Budget, text_fields=['notes'])
        sanitized += self.sanitize(CifCommon, name_fields=['staff_name'], text_fields=['officer_name','case_notes'])
        sanitized += self.sanitize(CifAttachmentCommon, file_fields=['attachment'], file_prefix='cif_attachments')
        sanitized += self.sanitize(IrfCommon, name_fields=['staff_name'], text_fields=['ims_case_number','case_notes','reason_for_intercept'])
        sanitized += self.sanitize(IrfAttachmentCommon, file_fields=['attachment'], file_prefix='scanned_irf_forms')
        sanitized += self.sanitize(MasterPerson, name_fields=['full_name'], text_fields=['notes'])
        sanitized += self.sanitize(Person, name_fields=['full_name','guardian_name'], phone_fields=['phone_contact'],
                text_fields=['master_set_notes', 'appearance', 'address_notes'])
        sanitized += self.sanitize(PersonAddress, text_fields=['address_notes'])
        sanitized += self.sanitize(PersonDocument, file_fields=['file_location'], file_prefix='person_documents')
        sanitized += self.sanitize(PersonIdentification, text_fields=['number'])
        sanitized += self.sanitize(PersonPhone, phone_fields=['number'])
        sanitized += self.sanitize(PersonSocialMedia, text_fields=['social_media'])
        sanitized += self.sanitize(VdfCommon, name_fields=['staff_name','who_victim_released_name'], phone_fields=['who_victim_released_phone'],
                text_fields=['where_victim_sent', 'case_notes'])
        sanitized += self.sanitize(VdfAttachmentCommon, file_fields=['attachment'], file_prefix='vdf_attachments')
        

        self.sanitize_email()
        self.create_test_users()

        self.stdout.write("Total sanitized {} objects".format(sanitized))
