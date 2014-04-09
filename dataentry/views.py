from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from django.contrib.auth.decorators import login_required
from dataentry.models import InterceptionRecord, Interceptee
from braces.views import LoginRequiredMixin
from dataentry.forms import InterceptionRecordForm


@login_required
def home(request):
    return render(request, 'home.html', locals())


class InterceptionRecordListView(LoginRequiredMixin, ListView):
    model = InterceptionRecord


class IntercepteeInline(InlineFormSet):
    model = Interceptee


class InterceptionRecordCreateView(LoginRequiredMixin, CreateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')


class InterceptionRecordUpdateView(LoginRequiredMixin, UpdateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
