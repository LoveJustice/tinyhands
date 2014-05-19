from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from django.contrib.auth.decorators import login_required
from dataentry.models import (
    VictimInterview,
    InterceptionRecord,
    Interceptee,
    VictimInterviewPersonBox,
    VictimInterviewLocationBox
)
from accounts.mixins import PermissionsRequiredMixin
from braces.views import LoginRequiredMixin
from dataentry.forms import (
    InterceptionRecordForm,
    VictimInterviewForm,
    VictimInterviewPersonBoxForm,
    VictimInterviewLocationBoxForm,
)


@login_required
def home(request):
    return render(request, 'home.html', locals())


class InterceptionRecordListView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ListView):
    model = InterceptionRecord
    permissions_required = ['permission_irf_view']


class IntercepteeInline(InlineFormSet):
    model = Interceptee
    extra = 12
    max_num = 12


class InterceptionRecordCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_add']


class InterceptionRecordUpdateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        UpdateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_edit']


class PersonBoxInline(InlineFormSet):
    model = VictimInterviewPersonBox
    extra = 3

    def get_factory_kwargs(self):
        kwargs = super(PersonBoxInline, self).get_factory_kwargs()
        kwargs['form'] = VictimInterviewPersonBoxForm
        return kwargs


class LocationBoxInline(InlineFormSet):
    model = VictimInterviewLocationBox
    extra = 2

    def get_factory_kwargs(self):
        kwargs = super(LocationBoxInline, self).get_factory_kwargs()
        kwargs['form'] = VictimInterviewLocationBoxForm
        return kwargs


class VictimInterviewListView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ListView):
    model = VictimInterview
    permissions_required = ['permission_vif_view']


class VictimInterviewCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = reverse_lazy('victiminterview_list')
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_add']


class VictimInterviewUpdateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        UpdateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = reverse_lazy('victiminterview_list')
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_edit']
