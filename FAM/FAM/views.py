from django.shortcuts import render
from accounts.models import Account

def home(request):
    return render(request, 'FAM/index.html', {"user":request.user})
