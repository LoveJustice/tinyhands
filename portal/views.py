from django.shortcuts import render


def main_dashboard(request):
    return render(request, "portal/main_dashboard.html")