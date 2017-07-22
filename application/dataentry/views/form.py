import json

from dataentry.models import Irf, IrfResponse, Form, Answer, Response
from braces.views import LoginRequiredMixin
from accounts.mixins import PermissionsRequiredMixin

from django.views.generic import CreateView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
'''
Assumptions for below are based on JSON coming in as such
{
    Form ID:         (456)
    Form Type:       (IRF)
    Storage:         (InterceptionRecord)
    Country:         (Nepal)
    Form #:          (BHW999)
    Date/Time Int:   (01/01/2000)

    Categories: [
        {
            Category ID:     (1)
            Type:            (Grid)
            Name:            (Who is in the group?)
            Responses: [
                [
                    {
                        Question ID:     (1)
                        Answer Type:     (Multiple Choice)
                        Answer ID:       (15)
                    }
                    ...
                ]
        },
        {
            Category ID:     (4)
            Type:            (Card)
            Name:            (Interceptee)
            Responses: [
                1: {
                        Question ID:     (4)
                        Answer Type:     (Open Response)
                        Answer:          (Rita Thapa)
                    }
                    ...
                    {
                        Question ID:     (8)
                        Answer Type:     (Address)
                        Answer:          (Kathmandu)
                    }
                2: {...}
            ]
        }
    ]
}
'''

# Right now assuming only IRFs
class IrfCreateView(LoginRequiredMixin, PermissionsRequiredMixin, CreateView, CreateWithInlinesView):
    model = Irf
    permissions_required = ['permission_irf_add']
    
    def save_form(self, request):
        form_data=json.loads(request.body)
        for category in form_data['Categories']:
            for response in category:
                # Get response and save
                pass
        return HttpResponse(render_to_string('dataentry/address1_create_success.html'))


# Not sure that this is actually needed since we are using JSON
class IrfResponseInline(InlineFormSet):
    model = IrfResponse

    def get_factory_kwargs(self):
        kwargs = super(IrfResponseInline, self).get_factory_kwargs()
        return kwargs