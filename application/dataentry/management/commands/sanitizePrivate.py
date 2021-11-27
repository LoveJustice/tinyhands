from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from dataentry.models import *
from accounts.models import Account, DefaultPermissionsSet
from budget.models import BorderStationBudgetCalculation
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
        'Paisley', 'Bella', 'London', 'Clara', 'Cadenc',
        'James', 'John', 'Robert', 'Michael', 'William',
        'David', 'Richard', 'Charles', 'Joseph', 'Thomas',
        'Christopher', 'Daniel', 'Paul', 'Mark', 'Donald',
        'George', 'Kenneth', 'Steven', 'Edward', 'Brian',
        'Ronald', 'Anthony', 'Kevin', 'Jason', 'Matthew',
        'Gary', 'Timothy', 'Jose', 'Larry', 'Jeffrey',
        'Frank', 'Scott', 'Eric', 'Stephen', 'Andrew',
        'Raymond', 'Gregory', 'Joshua', 'Jerry', 'Dennis',
        'Walter', 'Patrick', 'Peter', 'Harold', 'Douglas',
        'Henry', 'Carl', 'Arthur', 'Ryan', 'Roger']
    
    addresses = [
        {"score": 100, "extent": {"xmax": 92.97545390100008, "xmin": 87.60145390100008, "ymax": 26.491670475000024, "ymin": 21.117670475000022}, "address": "Bangladesh", "location": {"x": 90.28845390100008, "y": 23.804670475000023}, "$$hashKey": "object:2255", "attributes": {}},
        {"score": 100, "extent": {"xmax": 4.654196889000049, "xmin": 0.024196889000049904, "ymax": 11.976949812000045, "ymin": 7.346949812000046}, "address": "Benin", "location": {"x": 2.33919688900005, "y": 9.661949812000046}, "$$hashKey": "object:2313", "attributes": {}},
        {"score": 100, "extent": {"xmax": 107.43371615200004, "xmin": 102.39571615200003, "ymax": 15.227188507000045, "ymin": 10.189188507000045}, "address": "Cambodia", "location": {"x": 104.91471615200004, "y": 12.708188507000045}, "$$hashKey": "object:2383", "attributes": {}},
        {"score": 100, "extent": {"xmax": 94.32832654800008, "xmin": 64.55832654800007, "ymax": 38.26437973500004, "ymin": 8.494379735000043}, "address": "India", "location": {"x": 79.44332654800007, "y": 23.379379735000043}, "$$hashKey": "object:2575", "attributes": {}},
        {"score": 100, "extent": {"xmax": 1.4742276580000286, "xmin": -3.9737723419999718, "ymax": 10.70499510700007, "ymin": 5.256995107000069}, "address": "Ghana", "location": {"x": -1.2497723419999716, "y": 7.980995107000069}, "$$hashKey": "object:2447", "attributes": {}},
        {"score": 100, "extent": {"xmax": 42.30969855200003, "xmin": 33.469698552000025, "ymax": 4.948430658000047, "ymin": -3.8915693419999524}, "address": "Kenya", "location": {"x": 37.88969855200003, "y": 0.5284306580000475}, "$$hashKey": "object:2743", "attributes": {}},
        {"score": 100, "extent": {"xmax": 36.991735613000024, "xmin": 31.489735613000025, "ymax": -10.75852235099993, "ymin": -16.26052235099993}, "address": "Malawi", "location": {"x": 34.24073561300003, "y": -13.50952235099993}, "$$hashKey": "object:2821", "attributes": {}},
        {"score": 100, "extent": {"xmax": 23.60349898400005, "xmin": 10.839498984000048, "ymax": -15.756976121999973, "ymin": -28.520976121999976}, "address": "Namibia", "location": {"x": 17.22149898400005, "y": -22.138976121999974}, "$$hashKey": "object:3045", "attributes": {}},
        {"score": 100, "extent": {"xmax": 87.00516346900005, "xmin": 80.88316346900004, "ymax": 31.32013770300008, "ymin": 25.19813770300008}, "address": "Nepal", "location": {"x": 83.94416346900005, "y": 28.25913770300008}, "$$hashKey": "object:3155", "attributes": {}},
        {"score": 100, "extent": {"xmax": 30.914312610000053, "xmin": 28.998312610000056, "ymax": -1.0403949569999593, "ymin": -2.9563949569999597}, "address": "Rwanda", "location": {"x": 29.956312610000055, "y": -1.9983949569999595}, "$$hashKey": "object:3213", "attributes": {}},
        {"score": 100, "extent": {"xmax": -10.268031778999955, "xmin": -13.316031778999957, "ymax": 10.082037771000046, "ymin": 7.034037771000045}, "address": "Sierra Leone", "location": {"x": -11.792031778999956, "y": 8.558037771000045}, "$$hashKey": "object:3337", "attributes": {}},
        {"score": 100, "extent": {"xmax": 113.75663313100003, "xmin": 92.37863313100004, "ymax": 57.52369147400007, "ymin": 36.14569147400007}, "address": "Mongolia", "location": {"x": 103.06763313100004, "y": 46.83469147400007}, "$$hashKey": "object:2933", "attributes": {}},
        {"score": 100, "extent": {"xmax": 32.37204994000003, "xmin": 17.798049940000034, "ymax": -21.710182287999977, "ymin": -36.284182287999975}, "address": "South Africa", "location": {"x": 25.085049940000033, "y": -28.997182287999976}, "$$hashKey": "object:3465", "attributes": {}},
        {"score": 100, "extent": {"xmax": 40.458322712000076, "xmin": 29.532322712000074, "ymax": -0.9754001329999591, "ymin": -11.90140013299996}, "address": "Tanzania", "location": {"x": 34.995322712000075, "y": -6.438400132999959}, "$$hashKey": "object:3615", "attributes": {}},
        {"score": 100, "extent": {"xmax": 35.134706651000066, "xmin": 29.536706651000067, "ymax": 4.312805689000037, "ymin": -1.2851943109999628}, "address": "Uganda", "location": {"x": 32.335706651000066, "y": 1.513805689000037}, "$$hashKey": "object:3765", "attributes": {}},
        {"score": 100, "extent": {"xmax": 33.547276749000034, "xmin": 26.221276749000037, "ymax": -15.353205470999978, "ymin": -22.679205470999978}, "address": "Zimbabwe", "location": {"x": 29.884276749000037, "y": -19.016205470999978}, "$$hashKey": "object:3809", "attributes": {}},
        ]


    number_strings = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    irf_file_prefix = 'scanned_irf_forms/'
    vif_file_prefix = 'scanned_vif_forms/'

    sample_files = [
        'sample_200dpi.pdf', 'sample_300dpi.pdf', 'sample_400dpi.pdf', 'sample_720dpi.pdf',
        'sample_240dpi.pdf', 'sample_360dpi.pdf', 'sample_600dpi.pdf', 'sample_800dpi.pdf']

    def sanitize(self, model, photo_fields=[], name_fields=[], phone_fields=[], file_fields=[], file_prefix=None, text_fields=[], address_fields = []):
        class_name = model.__name__
        processed = 0
        main_name_field = None
        prior_name = None
        prior_replacement = None
        
        qs =  model.objects.all()
        if len(name_fields) > 0:
            main_name_field = name_fields[0]
            qs = qs.order_by(main_name_field)

        for instance in qs:
            modified = False

            # Sanitize images
            for field_name in photo_fields:
                try:
                    value = getattr(instance, field_name)
                    if value is None or value == '':
                        continue
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
                        if field_name == main_name_field:
                            if value != prior_name:
                                prior_name = value
                                prior_replacement = self.generate_name()
                            setattr(instance, field_name, prior_replacement)
                        else:
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
            
            for field_name in text_fields:
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
            
            for field_set in address_fields:
                address_field_name = field_set['address']
                longitude_field_name = field_set['longitude']
                latitude_field_name = field_set['latitude']
                
                value = getattr(instance, address_field_name)
                if value is not None and value != '' and getattr(instance,longitude_field_name) is not None and getattr(instance, latitude_field_name) is not None:
                    new_addr = self.select_address(getattr(instance,longitude_field_name), getattr(instance, latitude_field_name))
                    setattr(instance, address_field_name, new_addr)
                    setattr(instance, longitude_field_name, new_addr['location']['x'])
                    setattr(instance, latitude_field_name, new_addr['location']['y'])
                    modified = True
                    

            if modified:
                instance.save()
                processed += 1

        self.stdout.write("Sanitize model {}: objects processed {}".format(class_name, processed))

        return processed

    def select_photo(self):
        new_photo = self.photo_prefix + random.choice(self.sample_photos)
        return new_photo
    
    def select_address(self, longitude, latitude):
        bestInBounds = False
        bestScore = 10000000
        bestAddress = None
        for address in self.addresses:
            if address['extent']['xmin'] <= longitude and address['extent']['xmax'] >= longitude and address['extent']['ymin'] <= latitude and address['extent']['ymax'] >= latitude:
                inBounds = True
            else:
                inBounds = False
            xdiff = longitude - address['location']['x']
            ydiff = latitude - address['location']['y']
            score = xdiff*xdiff + ydiff*ydiff
            
            if bestInBounds:
                if inBounds and score < bestScore:
                    bestScore = score
                    bestAddress = address
            else:
                if inBounds or score < bestScore:
                    bestScore = score
                    bestAddress = address
        
        return bestAddress   

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
    
    def set_master_person_name(self):
        mps = MasterPerson.objects.all()
        for mp in mps:
            children = mp.person_set.all().order_by('master_set_date')
            if len(children) > 0:
                mp.full_name = children[0].full_name
            else:
                mp.full_name = self.generate_name()
            mp.save()

    def create_super(self):
        account = self.create_base_user()
        account = self.add_all_permissions(account)
        account.is_superuser = True
        account.permission_accounts_manage = True
        account.is_staff = True
        return account
    
    def all_permissions(self, account):
        perms = Permission.objects.all()
        for perm in perms:
            ulp = UserLocationPermission()
            ulp.account = account
            ulp.country = None
            ulp.station = None
            ulp.permission = perm
            ulp.save()

    def create_test_users(self):
        account = self.create_super()
        account.first_name = 'super'
        account.email = 'test_sup@example.com'
        account.set_password('pass')
        try:
            account.save()
        except IntegrityError:
            self.stderr.write("There is an existing user with email {}".format(account.email))
        
        self.all_permissions(account)

        account = self.create_base_user()
        account = self.add_all_permissions(account)
        account.first_name = 'test1'
        account.email = 'test1@example.com'
        account.set_password('pass')
        try:
            account.save()
        except IntegrityError:
            self.stderr.write("There is an existing user with email {}".format(account.email))
        
        self.all_permissions(account)

    def handle(self, *args, **options):
        sanitized = 0
        # Clean old forms
        Interceptee.objects.all().delete()
        InterceptionRecord.objects.all().delete()
        VictimInterviewPersonBox.objects.all().delete()
        VictimInterviewLocationBox.objects.all().delete()
        VictimInterview.objects.all().delete()

        sanitized += self.sanitize(BorderStationBudgetCalculation, text_fields=['notes'])
        sanitized += self.sanitize(CifCommon, name_fields=['staff_name'], text_fields=['officer_name','case_notes'])
        sanitized += self.sanitize(CifAttachmentCommon, file_fields=['attachment'], file_prefix='cif_attachments/')
        sanitized += self.sanitize(IrfCommon, name_fields=['staff_name'], text_fields=['ims_case_number','case_notes','reason_for_intercept'])
        sanitized += self.sanitize(IrfAttachmentCommon, file_fields=['attachment'], file_prefix='scanned_irf_forms/')
        sanitized += self.sanitize(LegalCase, text_fields=['lawyer_name'],phone_fields=['lawyer_phone'])
        sanitized += self.sanitize(LegalCaseTimeline, text_fields=['comment'])
        sanitized += self.sanitize(LegalCaseVictim, phone_fields=['alternate_phone'])
        sanitized += self.sanitize(LocationBoxCommon, text_fields=['address_notes'], address_fields=[{'address':'address','longitude':'longitude','latitude':'latitude'}])
        sanitized += self.sanitize(MasterPerson,  text_fields=['notes'])
        sanitized += self.sanitize(Person, photo_fields=['photo'], name_fields=['full_name','guardian_name'], phone_fields=['phone_contact'],
                text_fields=['master_set_notes', 'appearance', 'address_notes'], address_fields=[{'address':'address','longitude':'longitude','latitude':'latitude'}])
        sanitized += self.sanitize(PersonAddress, text_fields=['address_notes'], address_fields=[{'address':'address','longitude':'longitude','latitude':'latitude'}])
        sanitized += self.sanitize(PersonDocument, file_fields=['file_location'], file_prefix='person_documents/')
        sanitized += self.sanitize(PersonIdentification, text_fields=['number'])
        sanitized += self.sanitize(PersonPhone, phone_fields=['number'])
        sanitized += self.sanitize(PersonSocialMedia, text_fields=['social_media'])
        sanitized += self.sanitize(VdfCommon, name_fields=['staff_name','who_victim_released_name'], phone_fields=['who_victim_released_phone'],
                text_fields=['why_sent_home_with_with_alarms', 'where_victim_sent_details', 'case_notes'])
        sanitized += self.sanitize(VdfAttachmentCommon, file_fields=['attachment'], file_prefix='vdf_attachments/')
        
        self.set_master_person_name()
        self.sanitize_email()
        self.create_test_users()

        self.stdout.write("Total sanitized {} objects".format(sanitized))
