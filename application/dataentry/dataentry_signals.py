import django.dispatch

irf_done = django.dispatch.Signal(providing_args=["irf_number", "irf", "interceptees", "interception_alert"])

vif_done = django.dispatch.Signal(providing_args=["vif_number", "vif"])
