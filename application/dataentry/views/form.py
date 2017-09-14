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

# JSON to client for form layout for new entry. Assumes language & form type are already sent to server
{
    # Form model
    Form ID:         (002)
    Form Type:       (IRF)
    Storage:         (InterceptionRecord)
    Language:        (English)

    # How do we get questions from basic form?
    Irf_Data: [
        Irf Number:             (Open Response)
        Interception Date:      (Date/Time)
        Number of Victims:      (Number)
        Number of Traffickers:  (Number)
    ]

    Categories: [
        {
            # Category model
            Type:            (Grid),
            Name:            (Who is in the group?),
            Order:           (1),
            Questions: [
                [
                    # Any Question with responses of yes & no could be considered checkbox
                    # How do we deal with questions that appear in the same box as other questions/category header?
                    
                    {
                        Question ID:     (2)
                        Display Text:    (Alone)
                        Answer Type:     (Checkbox) 
                        Layout:          ("1.1")
                    },
                    {
                        Question ID:     (3)
                        Display Text:    (Is meeting a someone just across border)
                        Answer Type:     (Checkbox) 
                        Layout:          ("1.1.1.1")
                    },
                    {
                        Question ID:     (4)
                        Display Text:    (Meeting someone she's seen in Nepal in the last month)
                        Answer Type:     (Checkbox) 
                        Layout:          ("1.1.1.2")
                    },
                    {
                        Question ID:     (5)
                        Display Text:    (Was travelling with someone not with her)
                        Answer Type:     (Checkbox) 
                        Layout:          ("1.1.2.1")
                    },
                    {
                        Question ID:     (6)
                        Display Text:    (Husband / Wife)
                        Answer Type:     (Checkbox)
                        Layout:          ("1.2")
                    },
                    {
                        Question ID:     (7)
                        Display Text:    (Married in the past 2 weeks)
                        Answer Type:     (Checkbox) 
                        Layout:          ("1.2.1.1")
                    },
                    {
                        Question ID:     (8)
                        Display Text:    (Married in the past 2-8 weeks)
                        Answer Type:     (Checkbox) 
                        Layout:          ("1.2.1.2")
                    },
                    ...
                    {
                        Question ID:     (11)
                        Display Text:    (Own brother, sister / relative)
                        Answer Type:     (Checkbox)
                        Layout:          ("1.3")
                    },
                    ...
                ],
            Prompts: [
                # Could we include green lights here by including a type (follow up / green light)?
                {
                    Display Text:       (Are you meeting someone in India?)
                    Layout:             ("1.1.1")
                },
                {
                    Display Text:       (Was she traveling with someone earlier?)
                    Layout:             ("1.1.2")
                },
                {
                    Display Text:       (Ask when she was married)
                    Layout:             ("1.2.1")
                },
                {
                    Display Text:       (Ask when they met)
                    Layout:             ("1.2.2")
                },
                {
                    Display Text:       (Check citizenship cards)
                    Layout:             ("1.3.1")
                }
            ],
            Condition: [
                {"type": "red", (3:"true"), 30},
                {"type": "red", (4:"true"), 20},
                {"type": "red", (5:"true"), 40},
                {"type": "red", (7:"true"), 15},
                {"type": "red", (8:"true"), 10},
                ...
            ]
        },
        ...
        {
            Type:            (Card),
            Name:            (Interceptees),
            Order:           (8),
            Questions: [
                {
                    Question ID:     (45),
                    Display Text:    (Victim / Trafficker),
                    Answer Type:     (Multiple Choice),
                    Options:         ({"Victim":"v", "Trafficker":"t"}),
                    Layout:          ("1.1")
                },
                {
                    Question ID:     (46),
                    Display Text:    (Full Name),
                    Answer Type:     (Open Response),
                    Layout:          ("1.2")
                },
                {
                    Question ID:     (47),
                    Display Text:    (Female / Male),
                    Answer Type:     (Multiple Choice),
                    Options:         ({"Female":"f", "Male":"m"}),
                    Layout:          ("1.3")
                },
                {
                    Question ID:     (48),
                    Display Text:    (Age),
                    Answer Type:     (Open Response),
                    Layout:          ("1.4")
                },
                {
                    Question ID:     (49),
                    Display Text:    (Address 1),
                    Answer Type:     (Address 1),
                    Layout:          ("1.5")
                },
                {
                    Question ID:     (50),
                    Display Text:    (Address 2),
                    Answer Type:     (Address 2),
                    Layout:          ("1.6")
                },
                {
                    Question ID:     (51),
                    Display Text:    (Phone Contact),
                    Answer Type:     (Open Response),
                    Layout:          ("1.7")
                },
                {
                    Question ID:     (52),
                    Display Text:    (Photo),
                    Answer Type:     (Photo),
                    Layout:          ("1.7")
                }
            ]
        },
        {
            Type:            (Grid),
            Name:            (Procedures),
            Order:           (9),
            Questions: [
                {
                    Question ID:     (111)
                    Display Text:    (Call Subcommittee Chair)
                    Answer Type:     (Checkbox)
                    Layout:          ("2")
                },
                {
                    Question ID:     (112)
                    Display Text:    (Call THN to cross-check the names (6223856))
                    Answer Type:     (Checkbox)
                    Layout:          ("3")
                },
                {
                    Question ID:     (113)
                    Display Text:    (No)
                    Answer Type:     (Checkbox)
                    Layout:          ("4.2")
                },
                {
                    Question ID:     (114)
                    Display Text:    (Yes)
                    Answer Type:     (Checkbox)
                    Layout:          ("4.3")
                },
                {
                    Question ID:     (114)
                    Display Text:    (If yes, write the # from the table above:)
                    Answer Type:     (Checkbox)
                    Layout:          ("4.3")
                },
                ...
                # Question is in different category but wanted to represent it
                {
                    Question ID:     (120)
                    Display Text:    (Rate from 1-5 (1 = not at all sure, 5 = absolutely sure))
                    Answer Type:     (Multiple Choice)
                    Options:         ({"1 - Not at all sure": 1, "2 - Unsure but suspects it": 2, "3 - Somewhat sure": 3, "4 - Very Sure": 4, "5 - Absolutely sure": 5})
                    Layout:          ("13")
                },
                ...
                {
                    Question ID:    (122)
                    Display Text:   (Attach scanned copy of form (pdf or image))
                    Answer Type:    (File)
                    Layout:         ("14")
                }
                
            ]
            Prompts: [
                {
                    Display Text:       (You must complete each of these procedures for this IRF to be considered correctly filled out. Tick each box to indicate that you have completed the procedure.)
                    Layout:             ("1")
                },
                # We probably want to reconfigure how this question is asked/stored but I thought this was an interesting way to display the current configuration
                {
                    Display Text:       (Had any name come up before?)
                    Layout:             ("4.1")
                },
            ]
        }
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