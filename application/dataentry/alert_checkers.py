from django.conf import settings

from datetime import datetime
from django.utils.timezone import make_aware
import logging
from django.dispatch import receiver

from fuzzywuzzy import process

from accounts.models import Alert

from dataentry.models import Interceptee, Person, FuzzyMatching

from dataentry_signals import irf_done



logger = logging.getLogger(__name__)


class VIFAlertChecker(object):
    def __init__(self, form, inlines):
        self.vif = form
        self.inlines = inlines

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
        if self.vif.calculate_strength_of_case_points() > 10:
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
        
    @staticmethod
    def handle_irf_done(sender, **kwargs):
        irf = kwargs.get("irf")
        interceptees = kwargs.get("interceptees")
        if irf is not None and interceptees is not None:
            IRFAlertChecker(irf, interceptees).check_them()
          

    def check_them(self):
        current_datetime = make_aware(datetime.now())
        days = abs((current_datetime - self.irf.date_time_of_interception).days)
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
        all_people = Interceptee.objects.all().exclude(interception_record=self.irf.id) #this looks like we need it
        # Get a list of all of their full_names for use of fuzzy_wuzzy
        people_dict = {obj: obj.person.full_name for obj in all_people}

        trafficker_list = []

        fuzzy_object = FuzzyMatching.objects.all()[0]

        trafficker_in_custody = self.trafficker_in_custody()

        for interceptee in self.interceptees:
            if interceptee.kind == 't':
                onePersonMatches = []
                tmplist =[]
                p=interceptee.person
                onePersonMatches= process.extractBests(p.full_name, people_dict, score_cutoff=fuzzy_object.person_cutoff, limit=fuzzy_object.person_limit)
                print(onePersonMatches)
                for match in onePersonMatches:
                    w= match[2].person
                    #per = Person.objects.get()
                    tuplematch=(match[1],w)
                    tmplist.append(tuplematch)
                tmplist.insert(0,(0,interceptee.person))
                trafficker_list.append(tmplist)
        if len(trafficker_list) > 0:
            Alert.objects.send_alert("Name Match",
                                     context={"irf": self.irf,
                                              "trafficker_list": trafficker_list,
                                              "trafficker_in_custody" : trafficker_in_custody})
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
            if intercep.kind == 't' and intercep.photo not in [None, '']:
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
        logger.debug("trafficker_in_custody=" + trafficker_in_custody)
        trafficker_in_custody_list = []
        if trafficker_in_custody is not None:
            traffickers = trafficker_in_custody.split(',')
            for trafficker_index in traffickers:
                if trafficker_index.isdigit() == True:
                    idx = int(trafficker_index) - 1
                    if idx >= 0 and idx < len(self.interceptees):
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
    
irf_done.connect(IRFAlertChecker.handle_irf_done, weak=False, dispatch_uid = "IRFAlertChecker")    
    
    
