from accounts.models import Alert


class VIFAlertChecker(object):

    def __init__(self, form, inlines):
        self.vif = form
        self.inlines = inlines

    def check_them(self):
        self.fir_filed_against()
        self.dofe_complaint_against()
        self.ten_or_more_case_points()

    def fir_filed_against(self):
        '''
        - Any time a VIF is submitted with the box checked for "FIR filed against __" on question 8.1. E-mail should
        include VIF number, which type of case has been filed and the name of the person it has been filed against.
        '''
        # import ipdb
        # ipdb.set_trace()
        if self.vif.cleaned_data.get("legal_action_against_traffickers_fir_filed") and self.vif.cleaned_data.get("legal_action_fir_against_value") != '':
            Alert.alert_objects.send_alert("fir filed against", context={"vif": self.vif.instance})

    def dofe_complaint_against(self):
        '''
        Any time a VIF is submitted with the box checked for "DoFE complaint against __" on question 8.1. E-mail should
        include VIF number, which type of case has been filed and the name of the person it has been filed against.
        '''
        # import ipdb
        # ipdb.set_trace()
        if self.vif.cleaned_data.get("legal_action_against_traffickers_dofe_complaint") and self.vif.cleaned_data.get("legal_action_dofe_against_value") != '':
            Alert.alert_objects.send_alert("dofe complaint against", context={"vif": self.vif.instance})

    def ten_or_more_case_points(self):
        '''
        Any time there are 10 or more Strength of Case points. E-mail should include VIF number, the number of SoC
        points and whether or not a legal case has been filed.
        '''
        pass

class IRFAlertChecker(object):

    def __init__(self, form, inlines):
        self.irf = form
        self.interceptees = inlines[0]
        self.IRF_data = form.cleaned_data

    def check_them(self):
        self.identified_trafficker()

    def trafficker_name_match(self):
        '''
        - Any time there is a trafficker name match from a separate interception. E-mail should include form number that
        was submitted, form number that the match came from, and the name and all personal identifiers from both forms.
        '''
        pass

    def identified_trafficker(self):
        '''
        Email Alerts to Investigators:
            Any time there is photo of a trafficker on the IRF and the response to question 9.7 is a 4 or a 5
            OR any time there is a photo of a trafficker and the Red Flag points calculated by the computer is 400 or higher.
            E-mail should include IRF number, trafficker's name, photo, and the reason for the alert.
        '''
        import ipdb


        trafficker_list = []
        for person in self.interceptees:
            if person.cleaned_data.get("kind")=='t' and person.cleaned_data.get('photo') not in [None,'']:
                trafficker_list.append(person.instance)


        ipdb.set_trace()
        if len(trafficker_list) > 0:
            if (self.IRF_data.get('how_sure_was_trafficking') >= 4) or (self.irf.instance.calculate_total_red_flags() >= 400):
                Alert.alert_objects.send_alert("Identified Trafficker", context={ "irf" : self.irf.instance, "trafficker_list" : trafficker_list })
