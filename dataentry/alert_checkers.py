from accounts.models import Alert


class VIFAlertChecker(object):

    def __init__(self, form, inlines):
        self.VIF_form = form
        self.inlines = inlines
        self.IRF_data = form.cleaned_data

    def check_them(self):
        pass


class IRFAlertChecker(object):

    def __init__(self, form, inlines):
        self.IRF_form = form
        self.interceptees = inlines[0]

    def check_them(self):
        self.identified_trafficker()

    def identified_trafficker(self):
        import ipdb
        ipdb.set_trace()

        intercepted_data = self.interceptees.cleaned_data
        if intercepted_data.get('how_sure_was_trafficking') >= 4:
            Alert.alert_objects.send_alert("Identified Trafficker")
        elif intercepted_data.get('photo') and self.IRF_form.instance.calculate_total_red_flags() >= 400:
            Alert.alert_objects.send_alert("Identified Trafficker")

