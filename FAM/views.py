from django.shortcuts import render
from accounts.models import Profile

def home(request):
    return render(request, 'FAM/base_site/index.html', {"user":request.user})
