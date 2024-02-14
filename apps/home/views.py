from django.shortcuts import render

from apps.iptv.models import Iptv


# Create your views here.

def home(request):
    return render(request, 'frontend/index.html')


def live(request):
    context= {'data': Iptv.objects.all()}
    return render(request, 'frontend/pages/live.html', context=context)


def custom_404_page(request, exception):
    return render(request, 'frontend/error-404.html')
