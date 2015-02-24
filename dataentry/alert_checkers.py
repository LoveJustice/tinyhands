from django.core import serializers
from accounts.models import Alert
from fuzzywuzzy import process
from dataentry import serializers
from dataentry.models import Interceptee
import json


class VIFAlertChecker(object):
    def __init__(self, form, inlines):
        self.vif = form
        self.inlines = inlines

    def check_them(self):
        self.fir_and_dofe_against()
        self.ten_or_more_case_points()

    def fir_and_dofe_against(self):
        """
        - Any time a VIF is submitted with the box checked for "FIR filed against __" or for "DoFE complaint against __" on question 8.1. E-mail should
        include VIF number, which type of case has been filed and the name of the person it has been filed against.
        """
        fir = self.vif.cleaned_data.get("legal_action_against_traffickers_fir_filed")
        fir_value = self.vif.cleaned_data.get("legal_action_fir_against_value")
        dofe = self.vif.cleaned_data.get("legal_action_against_traffickers_dofe_complaint")
        dofe_value = self.vif.cleaned_data.get("legal_action_dofe_against_value")
        points = self.vif.instance.calculate_strength_of_case_points()

        if (fir and fir_value != '') and (dofe and dofe_value != ''):
            Alert.objects.send_alert("fir and dofe against", context={"vif": self.vif.instance, "both": True, "points": points, "fir_value": fir_value, "dofe_value": dofe_value})
            return True
        if fir and fir_value != '':
            Alert.objects.send_alert("fir and dofe against", context={"vif": self.vif.instance, "fir": True, "fir_value": fir_value, "points": points})
            return True
        if dofe and dofe_value != '':
            Alert.objects.send_alert("fir and dofe against", context={"vif": self.vif.instance, "dofe": True, "points": points, "dofe_value": dofe_value})
            return True
        return False

    def ten_or_more_case_points(self):
        """
        Any time there are 10 or more Strength of Case points. E-mail should include VIF number, the number of SoC
        points and whether or not a legal case has been filed.
        """
        fir = self.vif.cleaned_data.get("legal_action_against_traffickers_fir_filed")
        dofe = self.vif.cleaned_data.get("legal_action_against_traffickers_dofe_complaint")
        reason_for_no = self.vif.instance.get_reason_for_no()
        points = self.vif.instance.calculate_strength_of_case_points()

        if self.vif.instance.calculate_strength_of_case_points() > 10:
            Alert.objects.send_alert("strength of case", context={"vif": self.vif.instance, "points": points, "fir": fir, "dofe": dofe, "reason_for_no": reason_for_no})
            return True
        return False


class IRFAlertChecker(object):
    def __init__(self, form, inlines):
        self.irf = form
        self.interceptees = inlines[0]
        self.IRF_data = form.cleaned_data

    def check_them(self):
        self.identified_trafficker()
        self.trafficker_name_match()

    def trafficker_name_match(self):
        """
        - Any time there is a trafficker name match from a separate interception. E-mail should include form number that
        was submitted, form number that the match came from, and the name and all personal identifiers from both forms.
        """
        all_people = Interceptee.objects.all()
        people_list = [person.canonical_name for person in all_people]
        matches = []
        trafficker_list = []
        people_dict = {obj: obj.canonical_name for obj in all_people}
        trafficker_list = []
        trafficker_in_custody = self.trafficker_in_custody()
        traffickers_and_their_matches = {}

        for person in self.interceptees:
            if person.cleaned_data.get("kind") == 't':
                trafficker_list.append(person.instance)
        if len(trafficker_list) > 0:
            for trafficker in trafficker_list:
                matches.append(process.extractBests(trafficker.canonical_name, people_list, score_cutoff=90, limit=10))

        trafficker_in_custody = self.IRF_data.get("trafficker_taken_into_custody")
        trafficker_name = ''
        taken_into_custody = 0
        if self.IRF_data.get("trafficker_taken_into_custody")=='':
            taken_into_custody = self.IRF_data.get("trafficker_taken_into_custody")
        if trafficker_in_custody is not None and taken_into_custody < len([there for there in self.interceptees.cleaned_data if there]):
            trafficker_name = self.interceptees.cleaned_data[int(self.IRF_data.get("trafficker_taken_into_custody")) - 1].get("canonical_name")

        if len(matches) > 0:
            Alert.objects.send_alert("Name Match", context={"irf": self.irf.instance, "matches": matches, "trafficker_in_custody": trafficker_name})
            traffickers_and_their_matches[trafficker.canonical_name] = process.extractBests(trafficker.canonical_name, people_dict, score_cutoff=89, limit=10)
        if len({person for person in traffickers_and_their_matches if len(traffickers_and_their_matches[person]) > 0}) > 0:
            Alert.objects.send_alert("Name Match", context={"irf": self.irf.instance, "traffickers_matches": traffickers_and_their_matches, "trafficker_in_custody": trafficker_in_custody})
            return True
        return False

    def identified_trafficker(self):
        """
        Email Alerts to Investigators:
            Any time there is photo of a trafficker on the IRF and the response to question 9.7 is a 4 or a 5
            OR any time there is a photo of a trafficker and the Red Flag points calculated by the computer is 400 or
            higher. E-mail should include IRF number, traffickers name, photo, and the reason for the alert.
        """
        trafficker_list = []
        for person in self.interceptees:
            if person.cleaned_data.get("kind") == 't' and person.cleaned_data.get('photo') not in [None, '']:
                trafficker_list.append(person.instance)

        trafficker_in_custody = self.trafficker_in_custody()
        red_flags = self.irf.instance.calculate_total_red_flags()
        certainty_points = self.IRF_data.get('how_sure_was_trafficking')
        if len(trafficker_list) > 0:
            if (certainty_points >= 4) and (red_flags >= 400):
                Alert.objects.send_alert("Identified Trafficker", context={"irf": self.irf.instance, "trafficker_list": trafficker_list, "both": True, "trafficker_in_custody": trafficker_in_custody, "red_flags": red_flags, "certainty_points": certainty_points})
                return True
            if certainty_points >= 4:
                Alert.objects.send_alert("Identified Trafficker", context={"irf": self.irf.instance, "trafficker_list": trafficker_list, "how_sure": True, "trafficker_in_custody": trafficker_in_custody, "certainty_points": certainty_points})
                return True
            if red_flags >= 400:
                Alert.objects.send_alert("Identified Trafficker", context={"irf": self.irf.instance, "trafficker_list": trafficker_list, "flags": True, "trafficker_in_custody": trafficker_in_custody, "red_flags": red_flags})
                return True
        return False

    def trafficker_in_custody(self):
        """
        Returns the value of the trafficker in custody on the IRF
        If there is not one, it returns False
        """
        trafficker_in_custody = self.IRF_data.get("trafficker_taken_into_custody")
        taken_into_custody = 0
        if self.IRF_data.get("trafficker_taken_into_custody") == '':
            taken_into_custody = self.IRF_data.get("trafficker_taken_into_custody")
        if trafficker_in_custody is not None and taken_into_custody < len([there for there in self.interceptees.cleaned_data if there]):
            return self.interceptees.cleaned_data[int(self.IRF_data.get("trafficker_taken_into_custody")) - 1].get("canonical_name")
        return False
