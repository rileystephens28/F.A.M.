from django.shortcuts import render, redirect
from accounts.models import Profile

def home(request):
    # if request.user.is_authenticated:
    #     return redirect('dashboard')
    return render(request, 'FAM/index.html', {"user":request.user})
