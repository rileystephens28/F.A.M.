from django.shortcuts import render

def home(request):
    return render(request, 'FAM/index.html', {"user":request.user})
