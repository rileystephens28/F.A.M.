from django.shortcuts import render, redirect
from accounts.models import Profile

def home(request):
    """ Displays home page to unauthenticated user """
    return render(request, 'FAM/index.html', {"user":request.user})
