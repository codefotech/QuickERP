from django.shortcuts import render, redirect, get_object_or_404
from apps.router.models import Router
from apps.seller.forms import SellerAddForm
from apps.seller.models import Seller
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.contrib import messages
from system.utils import CommonFunction, get_app_urls, paginate_data


def index(request, *args, **kwargs):
    get_app_urls()
    return render(request, 'backend/main/seller/index.html')


def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'mobile', 'email', 'wallet']

    reverse = False
    query = Seller.objects.filter(admin_id=request.user.id, user__user_status=1).all()
    search_value = request.GET.get('search[value]')
    if search_value:
        query = Seller.objects.search_by_data(search_value).filter(admin_id=request.user.id, user__user_status=1)

    if request.user.user_type == "SA-2002":
        query = Seller.objects.all()
        if search_value:
            query = Seller.objects.search_by_data(search_value)

    order_column = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'asc')
    data = query
    if columns[order_column]:
        if order_dir == 'desc':
            reverse = True
        data = sorted(data, key=lambda p: getattr(p, columns[order_column]), reverse=reverse)
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
        'recordsTotal': query.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1

        action_html = f'<a href="/sellers/edit/{data.id}" class="" > <i class="fas fa-edit primary-icon"></i> </a>'

        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.user.username,
            'email': data.user.email,
            'mobile': data.user.user_mobile,
            'wallet': data.user.wallet_balance+' TK',
            'status': data.user.user_status,
            'action': mark_safe(action_html),

        })
    # f'<a href="/user/edit/{data.id}" class="btn btn-xs btn-primary"><i class="fa fa-edit"></i> Edit</a>'

    return JsonResponse(response_data)


def add(request):
    context = {}
    query = Router.objects.filter(admin_id=request.user.id).all()
    context['router_data'] = CommonFunction.model_to_dict(model=Router, query=query, key='id', value='name')
    form = SellerAddForm()

    if request.method == 'POST':
        form = SellerAddForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('/sellers')
        # elif form.errors:
            # messages.error(request, form.errors)
    context['form'] = form
    return render(request, 'backend/main/seller/add.html', context=context)


def edit(request, id=None):
    context = {}
    if id is not None:
        seller = get_object_or_404(Seller, id=id)
    else:
        seller = None

    if request.method == 'POST':
        form = SellerAddForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            return redirect('seller_list')
    else:
        form = SellerAddForm(instance=seller)
    query = Router.objects.filter(admin_id=request.user.id).all()
    context['router_data'] = CommonFunction.model_to_dict(model=Router, query=query, key='id', value='name')
    context['data'] = seller
    context['form'] = form
    return render(request, 'backend/main/seller/edit.html', context=context)




def seller_package_data(request):
    # query = Seller
    # data = paginate_data(Seller,)
    pass

# def iptv(request):
#     return render(request, 'backend/main/router/iptv.html')
# def hotspot_profile(request):
#     return render(request, 'backend/main/router/hotspot_profiles.html')
# def activation(request):
#     return render(request, 'backend/main/router/activation.html')
# def customer_list(request):
#     return render(request, 'backend/main/router/customer_list.html')
# def all_seller(request):
#     return render(request, 'backend/main/router/all_seller.html')
# def assign_profiles(request):
#     return render(request, 'backend/main/router/assign_profiles.html')
# def assign_vlans(request):
#     return render(request, 'backend/main/router/assign_vlans.html')
# def payouts(request):
#     return render(request, 'backend/main/router/payouts.html')
# def payouts_requests(request):
#     return render(request, 'backend/main/router/payouts_requests.html')
# def seller_verification_form(request):
#     return render(request, 'backend/main/router/seller_verification_form.html')
