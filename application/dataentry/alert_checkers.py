import logging
import traceback
import json
from datetime import datetime

from django.conf import settings
from django.utils.timezone import make_aware
from fuzzywuzzy import process

from accounts.models import Alert
from dataentry.models import Interceptee, SiteSettings, RedFlags, FormCategory
from .dataentry_signals import irf_done
from .dataentry_signals import vif_done
from .dataentry_signals import form_done

logger = logging.getLogger(__name__)


class VIFAlertChecker(object):
    def __init__(self, vif):
        self.vif = vif

    @staticmethod
    def handle_vif_done(sender, **kwargs):
        vif = kwargs.get("vif")
        if vif is not None:
            VIFAlertChecker(vif).check_them()

    def check_them(self):
        self.fir_and_dofe_against()
        self.ten_or_more_case_points()

    def fir_and_dofe_against(self):
        """Any time a VIF is submitted with the box checked for "FIR filed against __" or for
        "DoFE complaint against __" on question 8.1.

        E-mail should include VIF number, which type of case has been filed and the name
        of the person it has been filed against.

        """
        fir = self.vif.legal_action_against_traffickers_fir_filed
        fir_value = self.vif.legal_action_fir_against_value
        dofe = self.vif.legal_action_against_traffickers_dofe_complaint
        dofe_value = self.vif.legal_action_dofe_against_value
        points = self.vif.calculate_strength_of_case_points()

        if (fir and fir_value != '') and (dofe and dofe_value != ''):
            Alert.objects.send_alert("fir and dofe against",
                                     context={"site": settings.SITE_DOMAIN,
                                              "vif": self.vif,
                                              "both": True,
                                              "points": points,
                                              "fir_value": fir_value,
                                              "dofe_value": dofe_value})
            return True
        if fir and fir_value != '':
            Alert.objects.send_alert("fir and dofe against",
                                     context={"site": settings.SITE_DOMAIN,
                                              "vif": self.vif,
                                              "fir": True,
                                              "fir_value": fir_value,
                                              "points": points})
            return True
        if dofe and dofe_value != '':
            Alert.objects.send_alert("fir and dofe against",
                                     context={"site": settings.SITE_DOMAIN,
                                              "vif": self.vif,
                                              "dofe": True,
                                              "points": points,
                                              "dofe_value": dofe_value})
            return True
        return False

    def ten_or_more_case_points(self):
        """Any time there are 10 or more Strength of Case points.

        E-mail should include VIF number, the number of SoC
        points and whether or not a legal case has been filed.

        """
        fir = self.vif.legal_action_against_traffickers_fir_filed
        dofe = self.vif.legal_action_against_traffickers_dofe_complaint

        if fir or dofe:
            legal_case = True
        else:
            legal_case = False

        reason_for_no = self.vif.get_reason_for_no()
        points = self.vif.calculate_strength_of_case_points()

        if points > 10:
            Alert.objects.send_alert("strength of case",
                                     context={"site": settings.SITE_DOMAIN,
                                              "vif": self.vif,
                                              "points": points,
                                              "legal_case": legal_case,
                                              "fir": fir,
                                              "dofe": dofe,
                                              "reason_for_no": reason_for_no})
            return True
        return False


class IRFAlertChecker(object):
    def __init__(self, form, inlines):
        self.irf = form
        self.interceptees = inlines[0]
        self.red_flags = None
        
    @staticmethod
    def handle_irf_done(sender, **kwargs):
        try:
            logger.debug('Enter handle_irf_done')
            irf = kwargs.get("irf")
            interceptees = kwargs.get("interceptees")
            if irf is not None and interceptees is not None:
                irfAlertChecker = IRFAlertChecker(irf, interceptees)
                irfAlertChecker.check_them()
                if 'interception_alert' in kwargs and kwargs['interception_alert'] == True:
                    logger.debug('Found interception_alert')
                    irfAlertChecker.create_interception_alerts()
                else:
                    logger.debug('interception_alert not present')
        except Exception:
            logger.warn("Exception thrown " + traceback.format_exc())

    def check_them(self):
        current_datetime = make_aware(datetime.now())
        days = abs((current_datetime - self.irf.date_of_interception).days)
        if days > settings.ALERT_INTERVAL_IN_DAYS:
            logger.info("The number of days since the interception date for IRF#=" + self.irf.irf_number + 
                        ' is greater than the configured limit of ' + str(settings.ALERT_INTERVAL_IN_DAYS) + 
                        '. Alert checking will not be done.')
            return
        
        self.trafficker_name_match()
        self.identified_trafficker()

    def trafficker_name_match(self):
        """Any time there is a trafficker name match from a separate interception.

        E-mail should include form number that was submitted, form number that the match
        came from, and the name and all personal identifiers from both forms.

        """
        # Get all of the interceptees from other IRFs
        all_people = Interceptee.objects.all().exclude(interception_record=self.irf.id)  # this looks like we need it
        # Get a list of all of their full_names for use of fuzzy_wuzzy
        people_dict = {obj: obj.person.full_name for obj in all_people}

        trafficker_list = []

        site_settings = SiteSettings.objects.all()[0]

        trafficker_in_custody = self.trafficker_in_custody()

        for interceptee in self.interceptees:
            if interceptee.person.role == 'Suspect':
                tmplist = []
                p = interceptee.person
                onePersonMatches = process.extractBests(p.full_name, people_dict, score_cutoff=site_settings.get_setting_value_by_name('person_cutoff'), limit=site_settings.get_setting_value_by_name('person_limit'))
                logger.debug(onePersonMatches)
                for match in onePersonMatches:
                    tmplist.append((match[1], match[2].person))
                tmplist.insert(0, (0, interceptee.person))
                trafficker_list.append(tmplist)
        if len(trafficker_list) > 0:
            Alert.objects.send_alert("Name Match",
                                     context={"irf": self.irf,
                                              "trafficker_list": trafficker_list,
                                              "trafficker_in_custody": trafficker_in_custody})
            return True
        return False
    
    def identified_trafficker(self):
        """Email Alerts to Investigators

        Any time there is photo of a trafficker on the IRF and the response to question
        9.7 is a 4 or a 5

        OR any time there is a photo of a trafficker and the Red Flag points calculated by
        the computer is 400 or higher.

        E-mail should include IRF number, traffickers name, photo, and the reason for the
        alert.

        """
        trafficker_in_custody = self.trafficker_in_custody()
        red_flags = self.irf.calculate_total_red_flags()
        certainty_points = self.irf.how_sure_was_trafficking
        trafficker_list = []
        for intercep in self.interceptees:
            if intercep.person.role == 'Suspect' and intercep.photo not in [None, '']:
                trafficker_list.append(intercep.person)

        if len(trafficker_list) > 0:
            if (certainty_points >= 4) and (red_flags >= 400):
                Alert.objects.send_alert("Identified Trafficker",
                                         context={"site": settings.SITE_DOMAIN,
                                                  "irf": self.irf,
                                                  "trafficker_list": trafficker_list,
                                                  "both": True,
                                                  "trafficker_in_custody": trafficker_in_custody,
                                                  "red_flags": red_flags,
                                                  "certainty_points": certainty_points})
                return True
            elif certainty_points >= 4:
                Alert.objects.send_alert("Identified Trafficker",
                                         context={"site": settings.SITE_DOMAIN,
                                                  "irf": self.irf,
                                                  "trafficker_list": trafficker_list,
                                                  "how_sure": True,
                                                  "trafficker_in_custody": trafficker_in_custody,
                                                  "certainty_points": certainty_points})
                return True
            elif red_flags >= 400:
                Alert.objects.send_alert("Identified Trafficker",
                                         context={"site": settings.SITE_DOMAIN,
                                                  "irf": self.irf,
                                                  "trafficker_list": trafficker_list,
                                                  "flags": True,
                                                  "trafficker_in_custody": trafficker_in_custody,
                                                  "red_flags": red_flags})
                return True
        return False
    
    def trafficker_in_custody(self):
        """
        Returns the value of the trafficker in custody on the IRF
        If there is not one, it returns empty string
        """
        traff_format = ''
        trafficker_in_custody = self.irf.trafficker_taken_into_custody
        trafficker_in_custody_list = []
        if trafficker_in_custody is not None:
            traffickers = trafficker_in_custody.split(',')
            for trafficker_index in traffickers:
                if trafficker_index.isdigit():
                    idx = int(trafficker_index) - 1
                    if 0 <= idx < len(self.interceptees):
                        trafficker_in_custody_list.append(self.interceptees[idx].person.full_name)
                    else:
                        logger.warn("trafficker index out of range:" + idx)
                elif trafficker_index != '':
                    logger.warn('Non numeric index=' + trafficker_index)
             
            if len(trafficker_in_custody_list) > 0:       
                for trafficker_index in range(0, len(trafficker_in_custody_list)-1):
                    if traff_format != '':
                        traff_format = traff_format + ', ' + trafficker_in_custody_list[trafficker_index]
                    else:
                        traff_format = trafficker_in_custody_list[trafficker_index]
                
                if traff_format == '':
                    # Only one trafficker in custody
                    traff_format = trafficker_in_custody_list[0] + ' was'
                else:
                    traff_format = traff_format + ' and ' + trafficker_in_custody_list[len(trafficker_in_custody_list)-1] + ' were'
                
        logger.info("trafficker_in_custody returning " + traff_format)
        return traff_format
    
    def create_interception_alerts(self):
        logger.debug('In create_interception_alerts')
        alert_dict = {}
        alert_dict['datetimeOfInterception'] = str(self.irf.date_of_interception)
        
        border = {}
        location = {}
        if self.irf.border_station != None:
            border['name'] = self.irf.border_station.station_name
            location['latitude'] = self.irf.border_station.latitude
            location['longitude'] = self.irf.border_station.longitude
        else:
            border['name'] = 'UNKNOWN'
            location['latitude'] = 0.0
            location['longitude'] = 0.0
        
        if self.irf.location != None:
            location['name'] = self.irf.location
        else:
            location['name'] = ''
        
        border['location'] = location
        alert_dict['borderStation'] = border
        
        red_flags = self.get_red_flags()
        logger.debug('red_flags=' + red_flags)
        alert_dict['redFlags'] = red_flags
        
                    
        for interceptee in self.interceptees:
            if interceptee.person.role == 'PVOT':
                logger.debug('Interceptee - ' + interceptee.person.full_name)
                  
                full_name = interceptee.person.full_name
                idx = full_name.find(' ')
                first_name = ''
                if idx > 0:
                    first_name = full_name[:idx]
                intercept = {}
                intercept['name'] = first_name
                intercept['age'] = interceptee.person.age                
                alert_dict['intercept'] = intercept
                
                interception_alert = InterceptionAlert()
                interception_alert.json = json.dumps(alert_dict)
                interception_alert.save()
                logger.debug('json=' + interception_alert.json)
    
    def get_red_flags(self):
        logger.debug('get_red_flags')
        item_limit = 3
        length_limit = 0
        site_settings = SiteSettings.objects.all()[0]
        
        try:
            item_limit = site_settings.get_setting_value_by_name('interception_alert_item_limit')
        except Exception:
            pass
        
        try:
            length_limit = site_settings.get_setting_value_by_name('interception_alert_length_limit')
        except Exception:
            pass
        
        red_flags = RedFlags.objects.order_by('priority')
        result = ''
        sep = ''
        item_count = 0
        for red_flag in red_flags:
            try:
                value = getattr(self.irf, red_flag.field)
                if value != None and value == True:
                    logger.debug("field=" + red_flag.field + " text=" + red_flag.text + " sep=" + sep)
                    if length_limit > 0 and len(result) + len(red_flag.text) + 2 > length_limit:
                        break
                    result += sep + red_flag.text
                    sep = ', ' 
                    item_count += 1
                    if item_limit > 0 and item_count >= item_limit:
                        break              
            except Exception:
                pass
            
        return result
    
class FormAlertChecker:
    def __init__(self, form_data, remove):
        self.form_data = form_data
        self.remove = remove
    
    def process(self):
        if self.form_data.form_object.get_form_type_name() == 'IRF':
            self.trafficker_name_match()
    
    def trafficker_name_match(self):
        my_interceptee_class = None
        form_categories = FormCategory.objects.filter(name='People', form__form_type__name='IRF')
        people_dict = {}
        for form_category in form_categories:
            storage = form_category.storage
            if storage is None:
                continue
            mod = __import__(storage.module_name, fromlist=[storage.form_model_name])
            card_class = getattr(mod, storage.form_model_name)
            
            if form_category.form.id == self.form_data.form.id:
                interceptees = card_class.objects.exclude(interception_record = self.form_data.form_object)
                my_interceptee_class = card_class
            else:
                interceptees = card_class.objects.all()
            
            for interceptee in interceptees:
                if interceptee.person is not None and interceptee.person.full_name is not None and interceptee.person.full_name != '':
                    people_dict[interceptee] = interceptee.person.full_name
        
        custody_list = []
        trafficker_list = []
        trafficker_in_custody_list = []
        site_settings = SiteSettings.objects.all()[0]
        
        my_interceptees = my_interceptee_class.objects.all()
        for interceptee in my_interceptees:
            if interceptee.person.role == 'Suspect':
                if interceptee.trafficker_taken_into_custody:
                    custody_list.append(interceptee.person.full_name)
                tmplist = []
                p = interceptee.person
                onePersonMatches = process.extractBests(p.full_name, people_dict, score_cutoff=site_settings.get_setting_value_by_name('person_cutoff'), limit=site_settings.get_setting_value_by_name('person_limit'))
                logger.debug(onePersonMatches)
                for match in onePersonMatches:
                    tmplist.append((match[1], match[2].person))
                tmplist.insert(0, (0, interceptee.person))
                trafficker_list.append(tmplist)
        
        trafficker_in_custody = self.format_trafficker_in_custody(custody_list)
        if len(trafficker_list) > 0:
            Alert.objects.send_alert("Name Match",
                                     context={"irf": self.form_data.form_object,
                                              "trafficker_list": trafficker_list,
                                              "trafficker_in_custody": trafficker_in_custody})
            return True
        return False
    
    def format_trafficker_in_custody(self, custody_list):
        traff_format = ''
        if len(custody_list) > 0:       
            for custody_index in range(0, len(custody_list)-1):
                if traff_format != '':
                    traff_format = traff_format + ', ' + custody_list[custody_index]
                else:
                    traff_format = custody_list[custody_index]
            
            if traff_format == '':
                # Only one trafficker in custody
                traff_format = custody_list[0] + ' was'
            else:
                traff_format = traff_format + ' and ' + custody_list[len(custody_list)-1] + ' were'
        
        return traff_format
        
    
    @staticmethod
    def process_form(sender, **kwargs):
        form_data = kwargs.get("form_data")
        remove = kwargs.get("remove")
        if remove is None:
            remove = False    
        if form_data is None:
            return
        
        checker = FormAlertChecker(form_data, remove)
        checker.process()
      
irf_done.connect(IRFAlertChecker.handle_irf_done, weak=False, dispatch_uid="IRFAlertChecker")
vif_done.connect(VIFAlertChecker.handle_vif_done, weak=False, dispatch_uid="VIFAlertChecker")
#form_done.connect(FormAlertChecker.process_form, weak=False, dispatch_uid="FormAlertChecker")
