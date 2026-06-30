from django.shortcuts import render



def home(request):
    """Renders the HTML workspace page"""
    return render(request, 'dashboard/home.html')

def admin_dashboard_view(request):
    return render(request, 'dashboard/admin_view.html')
