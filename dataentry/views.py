from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from dataentry.models import InterceptionRecord
from braces.views import LoginRequiredMixin
from dataentry.forms import InterceptionRecordForm


@login_required
def home(request):
    return render(request, 'home.html', locals())


class InterceptionRecordListView(LoginRequiredMixin, ListView):
    model = InterceptionRecord


class InterceptionRecordCreateView(LoginRequiredMixin, CreateView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')


class InterceptionRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
