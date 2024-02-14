from django.urls import path, include

urlpatterns = [
    path('ipv4_calculator/', include('system.feature.ipv4_calculator.urls')),
    path('logs/', include('system.feature.logs.urls'))
    ]