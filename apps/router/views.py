from django.shortcuts import render, redirect, get_object_or_404
from apps.router.models import Router
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from apps.router.forms import RouterAddForm
from apps.router.router_os.routing import check_router_status, check_router_connection
from system.router.connect import MikroTikManager
from system.router.main import Microtik
from django.http import JsonResponse
import json

from system.router.ssh_router import MikroTikSSHManager


def index(request, *args, **kwargs):
    return render(request, 'backend/main/router/index.html')


def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'ip_address', 'api_port', 'username']

    reverse = False
    query = Router.objects.filter(admin_id=request.user.id, status=1).all()
    search_value = request.GET.get('search[value]')

    if search_value:
        query = Router.objects.search_by_router_data(search_value).filter(admin_id=request.user.id, status=1)

    if request.user.user_type == "SA-2002":
        query = Router.objects.filter(status=1).all()
        if search_value:
            query = Router.objects.search_by_router_data(search_value).filter(status=1)

    order_column = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')

    # Map the column index to the column name

    data = query
    if columns[order_column]:
        if order_dir == 'desc':
            reverse = True
        data = sorted(data, key=lambda p: getattr(p, columns[order_column]), reverse=reverse)
    # Paginate data
    if request.GET.get('start') and request.GET.get('length'):
        page = int(request.GET.get('start')) // int(request.GET.get('length')) + 1
    else:
        page = 0

    per_page = str(request.GET.get('length') if request.GET.get('length') else 25)
    paginator = Paginator(data, per_page)
    page_data = paginator.get_page(page)

    # Build response data
    response_data = {
        'draw': request.GET.get('draw'),
        'recordsTotal': Router.objects.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1

        action_html = f'<a href="/routers/edit/{data.id}" class="" > <i class="fas fa-edit primary-icon"></i> </a>'
        active_status = '<i class="fa-solid fa-circle text-success"></i>'
        status = '<button class="btn btn-success">Connected</button>'
        active_status_val = 1

        if not check_router_status(data.id):
            active_status = '<i class="fa-solid fa-circle text-danger"></i>'
            active_status_val = 0

        # connection = MikroTikManager(ip=data.ip_address, username=data.user_name, password=data.password,
        #                                 port=data.api_port)

        connection = MikroTikSSHManager.connect_router(router_ip=data.ip_address, username=data.user_name,
                                                       password=data.password,
                                                       port=data.ssh_port)

        if not connection:
            status = '<button class="btn btn-danger">Disconnected</button>'

        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.name,
            'ip_address': data.ip_address,
            'api_port': data.api_port,
            'user_name': data.user_name,
            'status': mark_safe(status),
            'active_status': mark_safe(active_status),
            'active_status_val': active_status_val,
            'action': mark_safe(action_html),

        })

    return JsonResponse(response_data)


def add(request):
    context = {}
    context['router_version_list'] = {
        'v1': 'Version 6.43 or older',
        'v2': 'Version greater 6.43 or older 7.0',
        'v3': 'Newer than version 7.0'
    }

    if request.method == 'POST':
        form = RouterAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/routers')
    else:
        form = RouterAddForm()
    context['form'] = form
    return render(request, 'backend/main/router/add.html', context=context)


def edit(request, id=None):
    context = {}
    if id is not None:
        router = get_object_or_404(Router, id=id)
    else:
        router = None

    if request.method == 'POST':
        form = RouterAddForm(request.POST, instance=router)
        if form.is_valid():
            form.save()
            return redirect('router_list')
    else:
        form = RouterAddForm(instance=router)
    context['data'] = router
    context['form'] = form
    return render(request, 'backend/main/router/edit.html', context=context)


def get_package_info_by_router(request):
    request_data = json.loads(request.body.decode('utf-8'))
    router_id = request_data.get('router_id')

    if router_id:
        router = Router.objects.get(id=router_id)
        ip = router.ip_address
        port = router.api_port
        username = router.user_name
        password = router.password
        try:
            conn = Microtik.connect(router_ip=ip, router_port=port, router_username=username,
                                    router_password=password)

            package_list = conn(cmd="/ppp/profile/print")
            if package_list:
                data = [{"name": item.get("name")} for item in package_list]
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({"error": f"error:{e}"}, status=400)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def get_router_active_status(request):
    if request.POST.get('data'):
        data = json.loads(request.POST.get('data'))
        router_data = {}
        for i in data:
            if check_router_status(i):
                router_data[i] = True
            else:
                router_data[i] = False

        return JsonResponse({'data': json.dumps(router_data)})


def router_import(request):
    return render(request, 'backend/main/router/import.html')


def hotspot_profile(request):
    return render(request, 'backend/main/router/others/hotspot_profiles.html')


def activation(request):
    return render(request, 'backend/main/router/activation.html')


def customer_list(request):
    return render(request, 'backend/main/router/others/customer_list.html')


def all_seller(request):
    return render(request, 'backend/main/router/others/all_seller.html')


def assign_profiles(request):
    return render(request, 'backend/main/router/others/assign_profiles.html')


def assign_vlans(request):
    return render(request, 'backend/main/router/others/assign_vlans.html')


def payouts(request):
    return render(request, 'backend/main/router/]/payouts.html')


def payouts_requests(request):
    return render(request, 'backend/main/router/]/payouts_requests.html')


def seller_verification_form(request):
    return render(request, 'backend/main/router/]/seller_verification_form.html')


def router_realtime_data(request):
    return render(request, 'backend/system/router/index.html')


def send_message_to_socket(request):
    context = {'user': f'{request.user.username if request.user.username else ""}'}
    return render(request, 'backend/system/router/send.html', context)
