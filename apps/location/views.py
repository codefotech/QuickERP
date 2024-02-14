from django.shortcuts import render


# Create your views here.

def countries(request):
    return render(request, 'backend/system/user/others/countries.html')


def states(request):
    return render(request, 'backend/system/user/states.html')


def cities(request):
    return render(request, 'backend/system/user/others/cities.html')


def zones(request):
    return render(request, 'backend/system/user/zones.html')
