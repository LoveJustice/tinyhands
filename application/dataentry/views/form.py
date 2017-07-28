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

The following would be the JSON for the form layout
{
    "form_id":
    "country_id":        // Is country_id displayed?  Does the client need to know?
    "categories":[
        "category_id":
        "type":
        "name":
        "order":        // Do we need this or is order in the array enough?
        "prompts": [
            {
                "prompt_description":
                "prompt_layout":
            }
        ],
        "questions": [
            {
                "question_id":
                "question_layout":
                "answer_type":
                "answers": [
                    {
                        "answer_id":
                        "answer_layout":
                        "answer_text":
                    }
                ]
            }
        ]
    ]
}

The following would be the JSON for the form data
{
    "form_id":
    "storage_id":
    "country":
    "base_form": [
        {
            "question_id":
            "answer_id":
            "storage_id":
        },
        {
            "question_id":
            "answer_text":
            "storage_id":
        },
        {
            "question_id":
            "answer_id":
            "answer_text":
            "storage_id":
        }
    ]
    "card_types": [
        {
            "category_id":
            "cards": [
                {
                    "storage_id":
                    "card_form": [                  
                        {
                            "question_id":
                            "answer_id":
                            "storage_id":
                        },
                        {
                            "question_id":
                            "answer_text":
                            "storage_id":
                        },
                        {
                            "question_id":
                            "answer_id":
                            "answer_text":
                            "storage_id":
                        }
                    ]
                }
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