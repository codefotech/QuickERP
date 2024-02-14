from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from system.all_utils.ip_address import get_ip_list_from_subnet


def ipv4_calculator(request):
    if request.method == 'POST':
        ip_address = request.POST.get('ip_address')
        if int(ip_address.split("/")[1]) <= 15 or int(ip_address.split("/")[1]) >= 33:
            return JsonResponse({'error': 'This subnet are not allowed'}, status=302)

        if ip_address:
            ip_addresses = get_ip_list_from_subnet(ip_address)
            count = len(ip_addresses)
            return JsonResponse({'success': True, 'data': {'count': count, 'ip_addresses': ip_addresses},
                                 'message': f'Total {count} IP found..'})

    else:
        return render(request, 'backend/system/ip_address/calculate.html')
