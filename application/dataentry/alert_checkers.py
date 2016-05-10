from django.conf import settings

from fuzzywuzzy import process

from accounts.models import Alert

from dataentry.models import Interceptee, Person


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

    def check_them(self):
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

        trafficker_in_custody = self.trafficker_in_custody()

        for interceptee in self.interceptees:
            if interceptee.cleaned_data.get("kind") == 't':
                onePersonMatches = []
                tmplist =[]
                p=interceptee.instance.person
                onePersonMatches= process.extractBests(p.full_name, people_dict, score_cutoff=89, limit = 10)
                print(onePersonMatches)
                for match in onePersonMatches:
                    w= match[2].person
                    #per = Person.objects.get()
                    tuplematch=(match[1],w)
                    tmplist.append(tuplematch)
                tmplist.insert(0,(0,interceptee.instance.person))
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
        for person in self.interceptees:
            if person.cleaned_data.get("kind") == 't' and person.cleaned_data.get('photo') not in [None, '']:
                trafficker_list.append(person.instance)



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
        If there is not one, it returns False
        """
        trafficker_in_custody = self.irf.trafficker_taken_into_custody
        taken_into_custody = 0
        if self.irf.trafficker_taken_into_custody == '':
            taken_into_custody = self.irf.trafficker_taken_into_custody
        if trafficker_in_custody is not None and taken_into_custody < len([there for there in self.interceptees.cleaned_data if there]):
            return self.interceptees.cleaned_data[int(self.irf.trafficker_taken_into_custody) - 1].get("full_name")
        return ''
