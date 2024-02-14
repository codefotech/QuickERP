from django.shortcuts import render, redirect, get_object_or_404

from apps.hotspot_router.models import HotspotRouter, UserHotspotRouter
from django.core.paginator import Paginator
from django.utils.safestring import mark_safe
from apps.hotspot_router.forms import HotspotRouterAddForm, HotspotRouterAssignForm
from apps.seller.models import Seller
from system.router.connect import MikroTikManager
from system.router.ssh_router import MikroTikSSHManager
from system.router.utils import check_hotspot_router_status
from django.http import JsonResponse
import json

from system.utils import CommonFunction, paginate_data


def index(request, *args, **kwargs):
    return render(request, 'backend/main/hotspot_router/index.html')


def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'ip_address', 'api_port', 'username']

    reverse = False

    query = HotspotRouter.objects.filter(admin_id=request.user.id, status=1).all()
    search_value = request.GET.get('search[value]')

    if search_value:
        query = HotspotRouter.objects.search_by_router_data(search_value).filter(admin_id=request.user.id, status=1)

    if request.user.user_type == "SA-2002":
        query = HotspotRouter.objects.all()
        if search_value:
            query = HotspotRouter.objects.search_by_router_data(search_value)

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
        'recordsTotal': HotspotRouter.objects.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1

        action_html = f'<a href="/hotspot_router/edit/{data.id}/" class="" > <i class="fas fa-edit primary-icon"></i> </a>'
        active_status = '<i class="fa-solid fa-circle text-success"></i>'
        status = '<button class="btn btn-success">Connected</button>'
        active_status_val = 1

        if not check_hotspot_router_status(data.id):
            active_status = '<i class="fa-solid fa-circle text-danger"></i>'
            active_status_val = 0

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
            'api_port': data.ssh_port,
            'user_name': data.user_name,
            'status': mark_safe(status),
            'active_status': mark_safe(active_status),
            'active_status_val': active_status_val,
            'action': mark_safe(action_html),

        })

    return JsonResponse(response_data)


def add(request):
    context = {}

    if request.method == 'POST':
        form = HotspotRouterAddForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hotspot_router_list')
    else:
        form = HotspotRouterAddForm()
    context['form'] = form
    return render(request, 'backend/main/hotspot_router/add.html', context=context)


def edit(request, id=None):
    context = {}
    if id is not None:
        router = get_object_or_404(HotspotRouter, id=id)
    else:
        router = None

    if request.method == 'POST':
        form = HotspotRouterAddForm(request.POST, instance=router)
        if form.is_valid():
            form.save()
            return redirect('hotspot_router_list')
    else:
        form = HotspotRouterAddForm(instance=router)
    context['data'] = router
    context['form'] = form
    return render(request, 'backend/main/hotspot_router/edit.html', context=context)


def assign_hotspot_router_list(request):
    if request.method == 'POST':
        if not request.user.user_type == 'SA-2002':
            data = UserHotspotRouter.objects.filter(admin_id=request.user.id).all()
        else:
            data = UserHotspotRouter.objects.all()

        response_data, page_data = paginate_data(UserHotspotRouter, data, request)

        count = 0
        for data in page_data:
            count = count + 1

            action_html = f'<a href="/hotspot_router/assign_hotspot_router/edit/{data.id}" class="" > <i class="fas fa-edit primary-icon"></i> </a>'

            response_data['data'].append({
                'count': count,
                'name': data.seller.user.name,
                'action': mark_safe(action_html),
            })
        return JsonResponse(response_data)

    return render(request, 'backend/main/hotspot_router/assign_router_list.html')


def assign_hotspot_router(request):
    context = {}
    if not request.user.user_type == 'SA-2002':
        query1 = HotspotRouter.objects.filter(admin_id=request.user.id, status=1)
        query2 = Seller.objects.filter(admin_id=request.user.id, user__user_status=1)
        context['router_data'] = CommonFunction.model_to_dict(model=HotspotRouter, key='id', value='name', query=query1)
        context['seller_data'] = CommonFunction.model_to_dict(model=Seller, key='id', value='user', query=query2)
    else:
        query1 = HotspotRouter.objects.filter(status=1)
        query2 = Seller.objects.filter(user__user_status=1)
        context['router_data'] = CommonFunction.model_to_dict(model=HotspotRouter, key='id', value='name', query=query1)
        context['seller_data'] = CommonFunction.model_to_dict(model=Seller, key='id', value='user', query=query2)

    if request.method == 'POST':
        form = HotspotRouterAssignForm(request.POST.copy())  # Create a mutable copy
        router_ids = request.POST.getlist('router_ids[]')
        form.data['router_list'] = router_ids
        if form.is_valid():
            form.save()
            return redirect('assign_hotspot_router_list')
    else:
        form = HotspotRouterAssignForm()

    context['form'] = form
    return render(request, 'backend/main/hotspot_router/assign_router.html', context=context)


def edit_assign_hotspot_router(request, id=None):
    context = {}

    if not request.user.user_type == 'SA-2002':
        query1 = HotspotRouter.objects.filter(admin_id=request.user.id, status=1)
        query2 = Seller.objects.filter(admin_id=request.user.id, user__user_status=1)
        context['router_data'] = CommonFunction.model_to_dict(model=HotspotRouter, key='id', value='name', query=query1)
        context['seller_data'] = CommonFunction.model_to_dict(model=Seller, key='id', value='user', query=query2)
    else:
        query1 = HotspotRouter.objects.filter(status=1)
        query2 = Seller.objects.filter(user__user_status=1)
        context['router_data'] = CommonFunction.model_to_dict(model=HotspotRouter, key='id', value='name', query=query1)
        context['seller_data'] = CommonFunction.model_to_dict(model=Seller, key='id', value='user', query=query2)

    if id is not None:
        user_hotspot_router = get_object_or_404(UserHotspotRouter, id=id)
    else:
        user_hotspot_router = None

    if request.method == 'POST':
        form = HotspotRouterAssignForm(request.POST.copy(), instance=user_hotspot_router)
        router_ids = request.POST.getlist('router_ids[]')
        form.data['router_list'] = router_ids

        if form.is_valid():
            form.save()
            return redirect('assign_hotspot_router_list')
    else:
        form = HotspotRouterAddForm(instance=user_hotspot_router)
    context['data'] = user_hotspot_router
    context['form'] = form
    return render(request, 'backend/main/hotspot_router/edit_assign_router.html', context=context)


def get_hotspot_router_active_status(request):
    if request.POST.get('data'):
        data = json.loads(request.POST.get('data'))
        router_data = {}
        for i in data:
            if check_hotspot_router_status(i):
                router_data[i] = True
            else:
                router_data[i] = False

        return JsonResponse({'data': json.dumps(router_data)})
