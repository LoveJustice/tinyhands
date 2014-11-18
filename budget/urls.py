from django.conf.urls import patterns, url
from budget import views

urlpatterns = patterns('portal.views',
    url(r'^budget_calculations/create$', views.BudgetCalcCreateView.as_view(), name='budget_create'),
    url(r'^budget_calculations/', views.BudgetCalcListView.as_view(), name='budget_list'),
    url(r'^getPDF/$', views.search_form),

)
