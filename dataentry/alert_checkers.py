from accounts.models import Alert


class VIFAlertChecker(object):

    def __init__(self, form, inlines):
        self.VIF_form = form
        self.inlines = inlines

    def check_them(self):
        pass


class IRFAlertChecker(object):

    def __init__(self, form, inlines):
        self.irf = form
        self.interceptees = inlines[0]
        self.IRF_data = form.cleaned_data

    def check_them(self):
        self.identified_trafficker()

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
