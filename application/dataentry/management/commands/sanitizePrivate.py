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

    def sanitize(self, model, photo_methods, name_methods, phone_methods, file_methods, file_prefix):
        class_name = model.__name__
        processed = 0

        for instance in model.objects.all():
            modified = False

            # Sanitize images
            for method_name in photo_methods:
                try:
                    value = getattr(instance, method_name)
                    if value is not None:
                        setattr(instance, method_name, self.select_photo())
                        modified = True
                except AttributeError as e:
                    print e
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)

            # Sanitize names
            for method_name in name_methods:
                try:
                    value = getattr(instance, method_name)
                    if value is not None:
                        setattr(instance, method_name, self.generate_name())
                        modified = True
                except AttributeError as e:
                    print e
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)

            # Sanitize phone numbers
            for method_name in phone_methods:
                try:
                    value = getattr(instance, method_name)
                    if value is not None:
                        setattr(instance, method_name, self.generate_phone(value))
                        modified = True
                except AttributeError as e:
                    print e
                except Exception as e:
                    self.stderr.write("WHAT?? {} - {}".format(type(e), e))
                    exit(1)
 
            # Sanitize scanned files
            for method_name in file_methods:
                try:
                    value = getattr(instance, method_name)
                    if value is not None:
                        setattr(instance, method_name, self.select_file(file_prefix))
                        modified = True
                except AttributeError as e:
                    print e
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
        cnt = 1

        for instance in Account.objects.all():
            instance.email = "thi_" + str(cnt) + "@example.com"
            instance.save()
            cnt += 1
        
    def create_base_user(self):
        account = Account()
        account.last_name = 'Test'
        localtime = time.localtime()
        account.last_login = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        account.joined = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        account.user_designation = DefaultPermissionsSet()
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

        account.permission_vdc_manage = True

        account.permission_budget_manage = True

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

        sanitized += self.sanitize(Interceptee, ['photo'], ['full_name'], ['phone_contact'], [], None)
        sanitized += self.sanitize(InterceptionRecord, [], [], [], ['scanned_form'], self.irf_file_prefix)
        sanitized += self.sanitize(VictimInterview, [],
                                   ['interviewer', 'victim_name', 'legal_action_fir_against_value', 'legal_action_dofe_against_value'],
                                   ['victim_phone', 'victim_guardian_phone'], ['scanned_form'], self.vif_file_prefix
                                   )
        sanitized += self.sanitize(VictimInterviewPersonBox, [], ['name'], ['phone'], [], None)
        sanitized += self.sanitize(VictimInterviewLocationBox, [], ['person_in_charge'], ['phone'], [], None)

        self.sanitize_email()
        self.create_test_users()

        self.stdout.write("Total sanitized {} objects".format(sanitized))
