from django.shortcuts import render, redirect, get_object_or_404
from apps.router.models import Router
from apps.reseller.forms import ReSellerAddForm
from apps.seller.models import Seller
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.contrib import messages
from system.utils import CommonFunction
from apps.seller.views import index as seller_index, add as seller_add


def index(request, *args, **kwargs):
    return render(request, 'backend/main/reseller/index.html')

def data_json_response(request, *args, **kwargs):
    columns = [None, 'name', 'mobile', 'email', 'wallet']

    reverse = False
    query = Seller.objects.all()
    if not request.user.user_type == 'SA-2002':
        query = Seller.objects.filter(admin_id=request.user.id)

    search_value = request.GET.get('search[value]')

    if search_value:
        query = Seller.objects.search_by_user_name(search_value)

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
        'recordsTotal': query.count(),
        'recordsFiltered': paginator.count,
        'data': []
    }

    count = 0
    for data in page_data:
        count = count + 1
        force_logout_btn = ''
        assign_parameters_btn = ''
        assign_desk_btn = ''
        park_assign = ''
        company_associated = ''
        access_log = ''

        action_html = f'<a href="/resellers/edit/{data.id}" class="" > <i class="fas fa-edit primary-icon"></i> </a>'

        response_data['data'].append({
            'count': count,
            'id': data.id,
            'name': data.user.username,
            'email': data.user.email,
            'mobile': data.user.user_mobile,
            'wallet': '000',
            'status': data.user.status,
            'action': mark_safe(action_html),

        })
    # f'<a href="/user/edit/{data.id}" class="btn btn-xs btn-primary"><i class="fa fa-edit"></i> Edit</a>'

    return JsonResponse(response_data)


def add(request):
    context = {}
    query = Router.objects.filter(admin_id=request.user.id).all()
    form = ReSellerAddForm()

    if request.method == 'POST':
        form = ReSellerAddForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('/resellers')
        elif form.errors:
            messages.error(request, form.errors)
    context['form'] = form
    return render(request, 'backend/main/reseller/add.html', context=context)



def edit(request, id=None):
    context = {}
    if id is not None:
        seller = get_object_or_404(Seller, id=id)
    else:
        seller = None

    if request.method == 'POST':
        form = ReSellerAddForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            return redirect('reseller_list')
    else:
        form = ReSellerAddForm(instance=seller)
    context['data'] = seller
    context['form'] = form
    return render(request, 'backend/main/reseller/edit.html', context=context)
