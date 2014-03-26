from django.shortcuts import render
from django.views.generic import ListView  # , CreateView, UpdateView, RedirectView
from django.contrib.auth.decorators import login_required
from dataentry.models import InterceptionRecord
from braces.views import LoginRequiredMixin


@login_required
def home(request):
    return render(request, 'home.html', locals())


class InterceptionRecordListView(LoginRequiredMixin, ListView):
    model = InterceptionRecord
